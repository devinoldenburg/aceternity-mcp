$ErrorActionPreference = 'Stop'

# Install via pipx (preferred) or pip
$pipx = Get-Command pipx -ErrorAction SilentlyContinue
if ($pipx) {
    Write-Host "Installing aceternity-mcp via pipx..."
    & pipx install aceternity-mcp
} else {
    Write-Host "pipx not found, installing via pip..."
    & python -m pip install aceternity-mcp
}
