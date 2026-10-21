$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$items = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'inventory.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$dest = Join-Path $PSScriptRoot 'rendered_ppt'
New-Item -ItemType Directory -Path $dest -Force | Out-Null
$app = New-Object -ComObject PowerPoint.Application
try {
    foreach ($item in $items) {
        if ($item.kind -ne '.pptx') { continue }
        $target = Join-Path $dest ($item.key + '.pdf')
        if (Test-Path -LiteralPath $target) { continue }
        $deck = $null
        try {
            $inputPath = Join-Path $root $item.source
            $normalized = Join-Path $dest ($item.key + '.pptx')
            if (Test-Path -LiteralPath $normalized) { $inputPath = $normalized }
            $deck = $app.Presentations.Open($inputPath, $true, $false, $false)
            $deck.SaveAs($target, 32)
            Write-Output ('EXPORTED ' + $item.source)
        } catch { Write-Output ('EXPORT_FAILED ' + $item.source + ': ' + $_.Exception.Message) } finally { if ($null -ne $deck) { $deck.Close() } }
    }
} finally { $app.Quit() }
