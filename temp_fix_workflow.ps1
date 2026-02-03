$ErrorActionPreference = 'Stop'
$filePath = '.github/workflows/clawbot-cron.yml'
$content = Get-Content -Path $filePath -Raw
$content = $content -replace 'pip install -r AgentTaskHub/requirements.txt', 'pip install -r requirements.txt'
$content = $content -replace 'python -3 -c', 'python -c'
Set-Content -Path $filePath -Value $content -Encoding UTF8
Write-Host "Workflow file updated successfully."