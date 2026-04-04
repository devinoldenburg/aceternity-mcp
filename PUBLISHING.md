# Publishing Guide

Complete guide for publishing aceternity-mcp to all supported registries.

## Automated (CI on release)

These publish automatically when you create a GitHub release:

| Registry | Workflow | Secret Required |
|---|---|---|
| PyPI | `publish.yml` | PyPI trusted publisher (OIDC) |
| Docker Hub | `docker-publish.yml` | `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` |
| ghcr.io | `docker-publish.yml` | `GITHUB_TOKEN` (automatic) |
| npm | `npm-publish.yml` | `NPM_TOKEN` |
| Snap Store | `snap-publish.yml` | `SNAP_STORE_TOKEN` |

## Manual (one-time submissions)

### MCP Directories

Submit to these web directories for MCP ecosystem visibility:

1. **Smithery** - https://smithery.ai/servers/new
   - `smithery.yaml` is already in the repo root
   - Submit GitHub URL: `https://github.com/devinoldenburg/aceternity-mcp`

2. **Glama** - https://glama.ai/mcp/servers
   - Click "Add Server" and submit the GitHub URL

3. **MCP.so** - https://mcp.so/submit
   - Submit name, GitHub URL, server config

4. **mcpservers.org** - https://mcpservers.org/submit
   - Submit GitHub URL

5. **MCPHub** - https://mcphub.io
   - Submit via web form

6. **PulseMCP** - https://pulsemcp.com
   - Submit via web form

7. **Cursor Directory** - https://cursor.directory/plugins/new
   - Submit as MCP plugin

### Homebrew

Create your own tap repository:

```bash
# 1. Create a new repo: homebrew-aceternity-mcp
gh repo create devinoldenburg/homebrew-aceternity-mcp --public

# 2. Copy the formula
cp packaging/homebrew/aceternity-mcp.rb Formula/aceternity-mcp.rb

# 3. Update the SHA256 (get from PyPI)
curl -sL https://pypi.org/pypi/aceternity-mcp/json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for f in data['urls']:
    if f['packagetype'] == 'sdist':
        print(f['digests']['sha256'])
"

# 4. Users install with:
brew tap devinoldenburg/aceternity-mcp
brew install aceternity-mcp
```

### conda-forge

```bash
# 1. Fork https://github.com/conda-forge/staged-recipes
# 2. Copy packaging/conda-forge/meta.yaml to recipes/aceternity-mcp/meta.yaml
# 3. Update SHA256 from PyPI
# 4. Submit PR
```

### AUR (Arch Linux)

```bash
# 1. Create AUR account at https://aur.archlinux.org
# 2. Clone AUR package: git clone ssh://aur@aur.archlinux.org/aceternity-mcp.git
# 3. Copy packaging/aur/PKGBUILD and update SHA256
# 4. Generate .SRCINFO: makepkg --printsrcinfo > .SRCINFO
# 5. Push to AUR
```

### Nix

```bash
# 1. Fork https://github.com/NixOS/nixpkgs
# 2. Add packaging/nix/default.nix to pkgs/by-name/ac/aceternity-mcp/package.nix
# 3. Update hash
# 4. Submit PR
```

### Scoop (Windows)

```bash
# 1. Create a bucket repo: devinoldenburg/scoop-aceternity-mcp
# 2. Copy packaging/scoop/aceternity-mcp.json to bucket/aceternity-mcp.json
# Users install with:
scoop bucket add aceternity-mcp https://github.com/devinoldenburg/scoop-aceternity-mcp
scoop install aceternity-mcp
```

### WinGet (Windows)

```bash
# 1. Fork https://github.com/microsoft/winget-pkgs
# 2. Copy packaging/winget/DevinOldenburg.AceternityMCP.yaml
#    to manifests/d/DevinOldenburg/AceternityMCP/1.8.1/
# 3. Update SHA256
# 4. Submit PR
```

### Chocolatey (Windows)

```bash
# 1. Create account at https://community.chocolatey.org
# 2. Get API key
# 3. Build and push:
cd packaging/chocolatey
choco pack
choco push aceternity-mcp.1.8.1.nupkg --source https://push.chocolatey.org/ --api-key YOUR_KEY
```

### Docker (manual)

```bash
docker build -t devinoldenburg/aceternity-mcp:1.8.1 .
docker push devinoldenburg/aceternity-mcp:1.8.1
docker tag devinoldenburg/aceternity-mcp:1.8.1 devinoldenburg/aceternity-mcp:latest
docker push devinoldenburg/aceternity-mcp:latest
```

## Required GitHub Secrets

Set these in Settings > Secrets and variables > Actions:

| Secret | For | How to get |
|---|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub | Docker Hub account username |
| `DOCKERHUB_TOKEN` | Docker Hub | Docker Hub > Account Settings > Security > New Access Token |
| `NPM_TOKEN` | npm | npmjs.com > Access Tokens > Generate |
| `SNAP_STORE_TOKEN` | Snap Store | `snapcraft export-login --snaps=aceternity-mcp -` |

## Release Checklist

1. Bump version in `pyproject.toml` and `src/aceternity_mcp/__init__.py`
2. Commit and push
3. Create annotated tag: `git tag -a v1.X.Y -m "v1.X.Y: description"`
4. Push tag: `git push origin v1.X.Y`
5. Create GitHub release (triggers all CI workflows)
6. Verify all workflows pass
