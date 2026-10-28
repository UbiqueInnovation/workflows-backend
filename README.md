# Shared Ubique Github Actions

## Reusable Workflows

A collection of reusable workflows needed for different projects.

### Usage

See [https://docs.github.com/en/actions/learn-github-actions/reusing-workflows#calling-a-reusable-workflow](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows#calling-a-reusable-workflow)

### R2 uploads and response headers

For R2, set `endpoint_url` to the R2 S3 API endpoint, `aws_region` to `auto`,
and use R2 access keys with the existing AWS secrets. Keep `public: false`.

Optional `cloudflare_zone_id`, `cloudflare_hostname`, `cloudflare_header_rules`
and the `cloudflare_api_token` secret configure response headers on the custom
domain. Rules are a JSON array of `{ "name": "assets", "paths": ["/*"],
"headers": { "Cross-Origin-Resource-Policy": "cross-origin" } }` objects.
Paths use case-sensitive URL wildcards; later rules override earlier headers.
Existing rules are preserved; obsolete rules must be removed manually.
The token needs Transform Rules Edit and Account Rulesets Read permissions.

## License

This project is licensed under the terms of the MPL 2 license. See the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
