"""
PUNTO DE ENTRADA
Ejecutar con:  py main.py

Estructura del proyecto:
    main.py       -> inicia la aplicación
    interfaz.py   -> ventana y widgets
    similitud.py  -> modelos de embeddings y cálculo de similitud
    texto.py      -> lectura de PDFs, tokenización, Jaccard, bloques
    config.py     -> modelos disponibles y parámetros
"""

from interfaz import App

if __name__ == "__main__":
    App().mainloop()