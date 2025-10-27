Write-Host "[info] Checking for Python 3.13..."
$py = "py"
$version = & $py -3.13 -V 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "[!] Python 3.13 not found by launcher. Install from python.org, or ensure 'py -3.13' works."
    exit 1
}
& $py -3.13 -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip wheel
Write-Host "[info] Installing requirements..."
python -m pip install -r requirements.txt
Write-Host "[OK] Environment ready."
Write-Host "To run: .\\.venv\\Scripts\\activate && python -m dcl_editor.app"
