"""
Crea un icono (icono.ico) y un acceso directo en el Escritorio que abre
main.py como una aplicación (sin ventana de consola).

Ejecutar UNA sola vez, con main.py en la misma carpeta:
    py crear_acceso_directo.py
"""

import os
import subprocess
import sys

CARPETA = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(CARPETA, "main.py")
ICONO = os.path.join(CARPETA, "icono.ico")
NOMBRE_ACCESO = "Detector de Similitud"


def asegurar_pillow():
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("Instalando Pillow (para generar el icono)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])


def crear_icono():
    from PIL import Image, ImageDraw

    tam = 256
    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Fondo: cuadrado redondeado azul
    d.rounded_rectangle((8, 8, tam - 8, tam - 8), radius=48, fill=(31, 106, 165, 255))

    # Dos "documentos" superpuestos
    d.rounded_rectangle((44, 52, 150, 190), radius=10, fill=(255, 255, 255, 235))
    d.rounded_rectangle((100, 78, 212, 216), radius=10, fill=(214, 234, 255, 255))

    # Líneas de texto en cada documento
    for y in (78, 102, 126, 150):
        d.line((60, y, 134, y), fill=(31, 106, 165, 255), width=7)
    for y in (106, 130, 154, 178):
        d.line((116, y, 196, y), fill=(31, 106, 165, 255), width=7)

    # Símbolo "=" (similitud) en un círculo naranja
    d.ellipse((150, 28, 232, 110), fill=(255, 146, 43, 255))
    d.line((168, 58, 214, 58), fill="white", width=9)
    d.line((168, 80, 214, 80), fill="white", width=9)

    img.save(
        ICONO,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"Icono creado: {ICONO}")


def crear_acceso_directo():
    # pythonw.exe ejecuta Python sin abrir la consola negra
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    ps = f"""
$desktop = [Environment]::GetFolderPath('Desktop')
$ruta = Join-Path $desktop '{NOMBRE_ACCESO}.lnk'
$ws = New-Object -ComObject WScript.Shell
$acc = $ws.CreateShortcut($ruta)
$acc.TargetPath = '{pythonw}'
$acc.Arguments = '"{SCRIPT}"'
$acc.WorkingDirectory = '{CARPETA}'
$acc.IconLocation = '{ICONO}'
$acc.Description = 'Detector de similitud de textos con embeddings'
$acc.Save()
Write-Output $ruta
"""
    resultado = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        print("No se pudo crear el acceso directo:")
        print(resultado.stderr)
        sys.exit(1)
    print(f"Acceso directo creado en: {resultado.stdout.strip()}")


if __name__ == "__main__":
    if os.name != "nt":
        print("Este script solo crea accesos directos en Windows.")
        sys.exit(1)
    if not os.path.exists(SCRIPT):
        print(f"No encuentro main.py en: {CARPETA}")
        sys.exit(1)
    asegurar_pillow()
    crear_icono()
    crear_acceso_directo()
    print("\nListo. Busca 'Detector de Similitud' en tu Escritorio.")