# Load API keys from ..\cd_.env (outside the repository) into the current session.
# Usage, from kit-td1:   . .\cd_load-env.ps1     (note the leading dot)
# Written with coding assistance (Claude Code). Contains no secret.
$envFile = Join-Path $PSScriptRoot "..\cd_.env"
if (-not (Test-Path $envFile)) {
    Write-Warning "No file $envFile : copy your keys there (NAME=value, one per line)."
    return
}
foreach ($line in Get-Content $envFile) {
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
        $name, $value = $Matches[1], $Matches[2].Trim('"')
        if ($value -match '\.\.\.$') { Write-Warning "$name still holds the placeholder"; continue }
        Set-Item -Path "env:$name" -Value $value
        Write-Host "$name loaded ($($value.Substring(0, [Math]::Min(6, $value.Length)))...)"
    }
}
