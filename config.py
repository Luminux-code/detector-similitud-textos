"/config.py"
"""
CONFIGURACIÓN
Aquí se definen los modelos disponibles y sus parámetros.
Para agregar un modelo nuevo, solo añade otra entrada a MODELOS.
"""

TITULO_APP = "Detector de Similitud de Textos con Embeddings"

MODELOS = {
    "MiniLM": {
        "nombre": "paraphrase-multilingual-MiniLM-L12-v2",
        "palabras_por_bloque": 60,   # tamaño de cada fragmento
        "umbral": 0.75,              # umbral inicial (editable en la interfaz)
        "max_seq": None,             # None = usa el límite por defecto del modelo
    },
    "BGE-M3": {
        "nombre": "BAAI/bge-m3",
        "palabras_por_bloque": 250,
        "umbral": 0.70,
        "max_seq": 1024,
    },
}