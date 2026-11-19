# Shared Ubique Github Actions

## Reusable Workflows

A collection of reusable workflows needed for different projects.

### Usage

See [https://docs.github.com/en/actions/learn-github-actions/reusing-workflows#calling-a-reusable-workflow](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows#calling-a-reusable-workflow)

### Upload a build artifact to S3

Build jobs run on separate runners from reusable workflows. To upload generated
files, first upload them with `actions/upload-artifact`, then call `s3_upload.yml`
with `needs` pointing to the build job. Set `artifact_to_upload` to the artifact's
name and `src_dir` to its download directory:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      # Set up your build tools and generate dist/ here.
      - uses: actions/upload-artifact@v7
        with:
          name: web-build
          path: dist/
          if-no-files-found: error

  upload:
    needs: build
    uses: UbiqueInnovation/workflows-backend/.github/workflows/s3_upload.yml@main
    with:
      aws_region: eu-central-1
      artifact_to_upload: web-build
      src_dir: dist
      dest_dir: 1.2.3
    secrets:
      aws_access_key_id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws_secret_access_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws_bucket: ${{ secrets.AWS_BUCKET }}
```

The named artifact must come from the current workflow run. Its contents are
downloaded directly into `src_dir`, so `dist/index.js` becomes
`s3://<bucket>/1.2.3/index.js`. Omitting `artifact_to_upload` keeps the existing
checkout-only upload behavior.

## License

This project is licensed under the terms of the MPL 2 license. See the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
