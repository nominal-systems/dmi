# Repository Guidelines

This repository contains documentation, infrastructure files and API specifications.

* Use **2 spaces** for indentation in all YAML, JSON and HCL/Terraform files.
* When modifying files under `spec/` run `npm run validate` inside that directory.
* For any Terraform changes run `terraform fmt -check` in the `terraform/` folder.
* Kubernetes manifests can be checked with `kubectl apply --dry-run=client -f <file>`.
* Docker compose files can be validated with `docker-compose config`.
* When editing `docs/` run `bundle exec jekyll build` to ensure the site builds.
* For scripts in `scripts/` install dependencies with `npm install` before running.

If commands fail because required tools are not installed or the environment lacks internet access, note it in your PR.
