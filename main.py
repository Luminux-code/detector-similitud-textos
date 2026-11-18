import threading
import webbrowser

from flask import Flask, jsonify, render_template, request

from config import MODELOS, TITULO_APP
from similitud import NOMBRES_METRICAS, calcular_similitud, obtener_modelo
from texto import leer_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # PDFs de hasta 30 MB


@app.get("/")
def index():
    return render_template(
        "index.html",
        titulo=TITULO_APP,
        modelos=list(MODELOS.keys()),
        metricas=NOMBRES_METRICAS,
    )


@app.post("/api/pdf")
def api_pdf():
    archivo = request.files.get("archivo")
    if not archivo:
        return jsonify(error="No se recibió ningún archivo"), 400
    try:
        texto = leer_pdf(archivo.stream)  # PdfReader acepta file-like, no hace falta guardar el PDF
    except Exception as e:
        return jsonify(error=f"No se pudo leer el PDF: {e}"), 400
    return jsonify(
        texto=texto,
        nombre=archivo.filename,
        palabras=len(texto.split()),
        sin_texto=len(texto.strip()) < 20,
    )


@app.post("/api/analizar")
def api_analizar():
    datos = request.get_json(silent=True) or {}
    t1 = (datos.get("texto1") or "").strip()
    t2 = (datos.get("texto2") or "").strip()
    clave = datos.get("modelo")

    if not t1 or not t2:
        return jsonify(error="Ingresa texto o sube un PDF en ambos paneles."), 400
    if clave not in MODELOS:
        return jsonify(error="Modelo no válido."), 400

    try:
        metricas, pares = calcular_similitud(t1, t2, clave)
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify(
        metricas=metricas,
        pares=[{"valor": v, "doc1": f1, "doc2": f2} for v, f1, f2 in pares],
    )


if __name__ == "__main__":
    # Precarga el primer modelo en segundo plano para que el primer análisis no tarde tanto
    threading.Thread(
        target=lambda: obtener_modelo(next(iter(MODELOS))), daemon=True
    ).start()
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)