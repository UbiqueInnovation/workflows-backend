import copy
import json
import os
from pathlib import Path
import subprocess
import textwrap
import unittest


WORKFLOW = (Path(__file__).parents[1] / ".github/workflows/s3_upload.yml").read_text()
SCRIPT = textwrap.dedent(WORKFLOW.split("python3 <<'PY'\n", 1)[1].split("\n          PY", 1)[0])
MODULE = {"__name__": "workflow_test"}
exec(compile(SCRIPT, "s3_upload.yml", "exec"), MODULE)
BUILD_RULES = MODULE["build_rules"]
SYNC_RULES = MODULE["sync_rules"]


class FakeAPI:
    def __init__(self, ruleset=None):
        self.ruleset = copy.deepcopy(ruleset)
        self.calls = []

    def __call__(self, method, path, body=None, missing_ok=False):
        self.calls.append((method, path, copy.deepcopy(body)))
        if method == "GET":
            return copy.deepcopy(self.ruleset)
        if path == "/rulesets":
            self.ruleset = {"id": "ruleset-id", "rules": [
                {**rule, "id": f"rule-{index}"} for index, rule in enumerate(body["rules"])
            ]}
        elif method == "POST":
            self.ruleset["rules"].append({**body, "id": f"rule-{len(self.ruleset['rules'])}"})
        elif method == "PATCH":
            rule_id = path.rsplit("/", 1)[1]
            self.ruleset["rules"] = [rule for rule in self.ruleset["rules"] if rule["id"] != rule_id]
            self.ruleset["rules"].append({**body, "id": rule_id})
        return copy.deepcopy(self.ruleset)


class HeaderRulesTest(unittest.TestCase):
    def setUp(self):
        self.config = [
            {"name": "all-assets", "paths": ["/*"], "headers": {
                "Cross-Origin-Resource-Policy": "cross-origin",
            }},
            {"name": "map-sdk", "paths": ["/*/assets/webmapsdk-*.js", "/*/assets/webmapsdk-*.wasm"],
             "headers": {"Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp"}},
        ]

    def build(self, config=None, host="assets.example.com", owner="example/components"):
        return BUILD_RULES(host, self.config if config is None else config, owner)

    def test_hostname_and_both_sdk_extensions_are_scoped(self):
        rules = self.build()
        self.assertEqual(rules[0]["expression"], '(http.host eq "assets.example.com") and (http.request.uri.path strict wildcard "/*")')
        self.assertIn('strict wildcard "/*/assets/webmapsdk-*.js" or ', rules[1]["expression"])
        self.assertIn('strict wildcard "/*/assets/webmapsdk-*.wasm"', rules[1]["expression"])
        self.assertEqual(rules[0]["action_parameters"]["headers"], {
            "cross-origin-resource-policy": {"operation": "set", "value": "cross-origin"},
        })

    def test_references_survive_value_changes_but_do_not_collide_between_hosts_or_repos(self):
        original = self.build()[0]["ref"]
        self.config[0]["headers"]["Cross-Origin-Resource-Policy"] = "same-origin"
        self.assertEqual(original, self.build()[0]["ref"])
        self.assertNotEqual(original, self.build(host="other.example.com")[0]["ref"])
        self.assertNotEqual(original, self.build(owner="example/other")[0]["ref"])

    def test_invalid_rules_fail_before_any_api_call(self):
        for config in ([], {}, [self.config[0], self.config[0]], [
            {"name": "bad", "paths": ["relative/*"], "headers": {"X-Test": "yes"}},
        ], [{"name": "bad", "paths": ["/*"], "headers": {"X-Test": "yes\r\nInjected: true"}}]):
            with self.subTest(config=config), self.assertRaises(ValueError):
                self.build(config)
        with self.assertRaises(ValueError):
            self.build(host="https://example.com/path")

    def test_missing_ruleset_is_created_with_both_rules(self):
        api = FakeAPI()
        SYNC_RULES(api, self.build())
        self.assertEqual([call[0] for call in api.calls], ["GET", "POST"])
        self.assertEqual(api.calls[1][2]["phase"], "http_response_headers_transform")
        self.assertEqual(len(api.ruleset["rules"]), 2)

    def test_rerun_updates_owned_rules_and_preserves_other_rules(self):
        unrelated = {"id": "unrelated", "ref": "manual", "action": "rewrite", "expression": "true"}
        api = FakeAPI({"id": "ruleset-id", "rules": [unrelated]})
        SYNC_RULES(api, self.build())
        self.config[0]["headers"]["Cross-Origin-Resource-Policy"] = "same-origin"
        SYNC_RULES(api, self.build())
        self.assertEqual(len(api.ruleset["rules"]), 3)
        self.assertEqual(api.ruleset["rules"][0], unrelated)
        self.assertEqual([rule["ref"] for rule in api.ruleset["rules"][1:]], [rule["ref"] for rule in self.build()])
        self.assertEqual([call[0] for call in api.calls], ["GET", "POST", "POST", "GET", "PATCH", "PATCH"])
        self.assertTrue(all(call[1].endswith(("rule-1", "rule-2")) for call in api.calls if call[0] == "PATCH"))


class UploadTest(unittest.TestCase):
    def upload(self, **overrides):
        script = textwrap.dedent(WORKFLOW.split('          args=(--recursive)\n', 1)[1])
        script = 'args=(--recursive)\n' + script
        stub = 'aws() { python3 -c \'import json,sys; print(json.dumps(sys.argv[1:]))\' "$@"; }\n'
        environment = {
            "PATH": os.environ["PATH"],
            "ENDPOINT_URL": "https://account.r2.cloudflarestorage.com",
            "SRC_DIR": "dist with spaces", "DEST_DIR": "1.2.3/", "BUCKET": "assets",
            "PUBLIC": "false", "CACHE_CONTROL": "public, max-age=31536000, immutable",
        }
        environment.update(overrides)
        result = subprocess.run(["bash", "-e", "-c", stub + script], env=environment,
                                check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_cli_keeps_endpoint_cache_control_and_paths_as_single_arguments(self):
        self.assertEqual(self.upload(), [
            "s3", "cp", "dist with spaces", "s3://assets/1.2.3/", "--recursive",
            "--endpoint-url", "https://account.r2.cloudflarestorage.com",
            "--cache-control", "public, max-age=31536000, immutable",
        ])

    def test_aws_upload_without_endpoint_preserves_public_acl(self):
        self.assertEqual(self.upload(ENDPOINT_URL="", CACHE_CONTROL="", PUBLIC="true"), [
            "s3", "cp", "dist with spaces", "s3://assets/1.2.3/", "--recursive", "--acl", "public-read",
        ])


if __name__ == "__main__":
    unittest.main()
