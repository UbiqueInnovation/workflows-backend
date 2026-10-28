# Shared Ubique Github Actions

## Reusable Workflows

A collection of reusable workflows needed for different projects.

### Usage

See [https://docs.github.com/en/actions/learn-github-actions/reusing-workflows#calling-a-reusable-workflow](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows#calling-a-reusable-workflow)

### R2 uploads and response headers

`s3_upload.yml` also supports Cloudflare R2 through the same AWS CLI upload.
Set `endpoint_url` to your R2 S3 API endpoint, set `aws_region` to `auto`, and
provide R2 access keys through the existing `aws_access_key_id` and
`aws_secret_access_key` secrets. Keep `public: false`: R2 does not support S3
object ACLs. Public access is configured on the bucket's custom domain instead.

For custom response headers, set the optional Cloudflare inputs below. Arbitrary
headers such as CORP, COOP and COEP cannot be set as response headers by an S3
upload. The workflow configures Cloudflare Response Header Transform Rules on
the custom domain, then uploads files with `aws s3 cp` as usual.

```yaml
upload:
  uses: UbiqueInnovation/workflows-backend/.github/workflows/s3_upload.yml@main
  with:
    aws_region: auto
    endpoint_url: https://ACCOUNT_ID.r2.cloudflarestorage.com
    src_dir: dist
    dest_dir: 1.2.3
    cache_control: public,max-age=31536000,immutable
    cloudflare_zone_id: ${{ vars.CLOUDFLARE_ZONE_ID }}
    cloudflare_hostname: assets.example.com
    cloudflare_header_rules: >-
      [
        {
          "name": "all-assets",
          "paths": ["/*"],
          "headers": {"Cross-Origin-Resource-Policy": "cross-origin"}
        },
        {
          "name": "map-sdk",
          "paths": ["/*/assets/webmapsdk-*.js", "/*/assets/webmapsdk-*.wasm"],
          "headers": {
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Embedder-Policy": "require-corp"
          }
        }
      ]
  secrets:
    aws_access_key_id: ${{ secrets.R2_ACCESS_KEY_ID }}
    aws_secret_access_key: ${{ secrets.R2_SECRET_ACCESS_KEY }}
    aws_bucket: ${{ secrets.R2_BUCKET }}
    cloudflare_api_token: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

`paths` are absolute public URL paths, not local `dist/` paths. They use
Cloudflare's case-sensitive `strict wildcard` matching (`*` includes `/`).
The examples match every release version, avoiding new rules for every tag.
Every rule also matches only `cloudflare_hostname`. Rules run in input order;
later rules override earlier values of the same header. Different headers are
combined, so the SDK files receive all three headers in this example.

The Cloudflare API token is separate from R2's S3 access keys. Give it
**Transform Rules > Edit** for the target zone and **Account Rulesets > Read**, as
described in Cloudflare's API documentation. The domain must already be connected
to the R2 bucket in the zone; this workflow does not configure DNS or bucket CORS.

Rules have stable references based on the calling repository, hostname and rule
name. Re-running updates those rules rather than creating duplicates. Existing
rules are preserved, and managed rules are placed at the end in input order.
Omitted or renamed rules are not deleted automatically; remove obsolete rules
in Cloudflare explicitly. With the default `cloudflare_header_rules: '[]'`, the
workflow makes no Cloudflare API calls. With no `endpoint_url`, it continues to
target AWS S3.

References: [R2 AWS CLI](https://developers.cloudflare.com/r2/examples/aws/aws-cli/),
[R2 S3 API compatibility](https://developers.cloudflare.com/r2/api/s3/api/),
[Cloudflare response header rules API](https://developers.cloudflare.com/rules/transform/response-header-modification/create-api/).

## License

This project is licensed under the terms of the MPL 2 license. See the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
