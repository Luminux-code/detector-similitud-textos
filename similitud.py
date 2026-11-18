from sentence_transformers import SentenceTransformer, util

from config import MODELOS
from texto import coseno_vectores, dividir_en_bloques, jaccard

NOMBRES_METRICAS = [
    "Jaccard (bruto)",
    "Jaccard (filtrado)",
    "Coseno (Count)",
    "Coseno (TF-IDF)",
    "Coseno (TF-IDF bigramas)",
    "Coseno (Embeddings)",
]

_cache_modelos = {}


def obtener_modelo(clave):
    if clave not in _cache_modelos:
        cfg = MODELOS[clave]
        modelo = SentenceTransformer(cfg["nombre"])
        if cfg["max_seq"]:
            modelo.max_seq_length = cfg["max_seq"]
        _cache_modelos[clave] = modelo
    return _cache_modelos[clave]


def calcular_similitud(texto1, texto2, clave_modelo):
    cfg = MODELOS[clave_modelo]
    modelo = obtener_modelo(clave_modelo)

    bloques1 = dividir_en_bloques(texto1, cfg["palabras_por_bloque"])
    bloques2 = dividir_en_bloques(texto2, cfg["palabras_por_bloque"])

    emb1 = modelo.encode(bloques1, convert_to_tensor=True, normalize_embeddings=True)
    emb2 = modelo.encode(bloques2, convert_to_tensor=True, normalize_embeddings=True)

    global_sim = util.cos_sim(emb1.mean(dim=0), emb2.mean(dim=0)).item()

    matriz = util.cos_sim(emb1, emb2)
    k = min(3, matriz.numel())
    valores, indices = matriz.flatten().topk(k)
    n2 = matriz.shape[1]
    pares = []
    for valor, idx in zip(valores.tolist(), indices.tolist()):
        i, j = divmod(idx, n2)
        pares.append((valor, bloques1[i], bloques2[j]))

    corpus = bloques1 + bloques2

    metricas = {
        "Jaccard (bruto)": jaccard(texto1, texto2, filtrado=False),
        "Jaccard (filtrado)": jaccard(texto1, texto2, filtrado=True),
        "Coseno (Count)": coseno_vectores(texto1, texto2, "count"),
        "Coseno (TF-IDF)": coseno_vectores(
            texto1, texto2, "tfidf", corpus=corpus
        ),
        "Coseno (TF-IDF bigramas)": coseno_vectores(
            texto1, texto2, "tfidf", (2, 2),
            quitar_stopwords=False, corpus=corpus,
        ),
        "Coseno (Embeddings)": global_sim,
    }
    return metricas, pares