$ErrorActionPreference = "Stop"

Write-Host "Instalando dependencias del notebook..."
python -m pip install -r "$PSScriptRoot\requirements.txt"

Write-Host "Registrando kernel de Jupyter: Python (Opti GA)"
python -m ipykernel install --user --name opti-ga --display-name "Python (Opti GA)"

Write-Host ""
Write-Host "Listo. En VS Code, abre el notebook y selecciona el kernel: Python (Opti GA)"
