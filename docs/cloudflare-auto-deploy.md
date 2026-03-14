# Cloudflare Auto Deploy

This repository now includes a GitHub Actions workflow for automatic Cloudflare deployments.

## What It Does

On every push to `main`, GitHub Actions will:

1. install dependencies for `frontend`, `admin`, and `cf-worker`
2. build `frontend` and `admin`
3. optionally apply the D1 schema when manually requested
4. deploy `cf-worker` with Wrangler
5. deploy `frontend/dist` to the Cloudflare Pages project
6. deploy `admin/dist` to the Cloudflare Pages project

The workflow file is:

- `.github/workflows/cloudflare-deploy.yml`

The shared deployment script is:

- `scripts/deploy/cloudflare-deploy.sh`

The deployment workflow targets a self-hosted Windows runner with these labels:

- `self-hosted`
- `Windows`
- `X64`
- `mojo-cloudflare`

## Required GitHub Secrets

Add this repository secret before enabling automatic deployment:

- `CLOUDFLARE_API_TOKEN`

The workflow already uses these repository defaults:

- Cloudflare account ID: `9f5aeb4079b42a826ae6756eee6774c8`
- frontend Pages project: `mojo-frontend`
- admin Pages project: `mojo-admin`
- D1 database: `mojo-prod`

Optional overrides:

- `CLOUDFLARE_FRONTEND_PROJECT`
  - default: `mojo-frontend`
- `CLOUDFLARE_ADMIN_PROJECT`
  - default: `mojo-admin`
- `CLOUDFLARE_D1_DATABASE`
  - default: `mojo-prod`

## Notes

- The workflow currently deploys production on pushes to `main`.
- Push deployments do not apply the D1 schema automatically.
- Manual `workflow_dispatch` runs can opt into D1 schema application when needed.
- Worker secrets such as API keys must already exist in Cloudflare. This workflow does not create or rotate Worker secrets.
- The current self-hosted runner is configured on a Windows machine and auto-starts at user login.

## Manual Run

You can also run the same deployment flow locally:

```bash
bash scripts/deploy/cloudflare-deploy.sh
```

Required local environment variables:

```bash
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=...
```

On Windows, run the script from Git Bash or WSL. The GitHub Actions workflow is the primary deployment path and does not require any local shell setup.
