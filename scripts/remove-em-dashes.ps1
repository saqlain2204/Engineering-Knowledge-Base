# Replace em dashes with spaced hyphens in all HTML files
$root = Split-Path -Parent $PSScriptRoot
$emDash = [char]0x2014
$count = 0

Get-ChildItem -Path $root -Filter '*.html' -Recurse | ForEach-Object {
  $content = [System.IO.File]::ReadAllText($_.FullName)
  if ($content.Contains($emDash)) {
    $newContent = $content.Replace($emDash, ' - ')
    [System.IO.File]::WriteAllText($_.FullName, $newContent)
    $count++
    Write-Host "Updated: $($_.FullName.Substring($root.Length + 1))"
  }
}

Write-Host "Done. Updated $count files."
