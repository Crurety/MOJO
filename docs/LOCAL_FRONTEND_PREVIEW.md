# Local Frontend Live Preview

## Quick Start (Windows PowerShell)

Run from project root:

```powershell
.\preview-frontend.ps1
```

The script will:

1. install `frontend` dependencies if needed
2. start Vite dev server with live reload
3. open browser at `http://localhost:5173`

## Manual Start

```powershell
cd frontend
npm ci
npm run dev:preview
```

## Optional Environment Variables

- `VITE_API_PROXY_TARGET`: backend API target for `/api` proxy
  - default: `http://127.0.0.1:8000`
- `VITE_USE_POLLING`: file watch polling mode (`true` or `false`)
  - default: `false`
  - set to `true` when filesystem events are unreliable (for example in some VM/docker/shared folder setups)
