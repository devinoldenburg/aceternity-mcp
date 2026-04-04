$ErrorActionPreference = 'Stop'

$pipx = Get-Command pipx -ErrorAction SilentlyContinue
if ($pipx) {
    & pipx uninstall aceternity-mcp
} else {
    & python -m pip uninstall -y aceternity-mcp
}
