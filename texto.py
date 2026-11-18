import re
import unicodedata

from nltk.corpus import stopwords
from pypdf import PdfReader
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^\w\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


# Se carga una sola vez al abrir el programa, ya normalizada (sin tildes)
STOP_ES = {normalizar(p) for p in stopwords.words("spanish")}


def leer_pdf(ruta):
    lector = PdfReader(ruta)
    paginas = [p.extract_text() or "" for p in lector.pages]
    return "\n".join(paginas)


def tokenizar(texto, quitar_stopwords=True, quitar_numeros=True):
    palabras = normalizar(texto).split()
    if quitar_stopwords:
        palabras = [p for p in palabras if p not in STOP_ES]
    if quitar_numeros:
        palabras = [p for p in palabras if not p.isdigit()]
    return set(palabras)


def jaccard(texto1, texto2, filtrado=True):
    # filtrado=False -> Jaccard bruto (con stopwords y números)
    # filtrado=True  -> Jaccard filtrado (sin stopwords ni números)
    s1 = tokenizar(texto1, quitar_stopwords=filtrado, quitar_numeros=filtrado)
    s2 = tokenizar(texto2, quitar_stopwords=filtrado, quitar_numeros=filtrado)
    union = s1 | s2
    return len(s1 & s2) / len(union) if union else 0.0


def coseno_vectores(texto1, texto2, tipo="count", ngram=(1, 1),
                    quitar_stopwords=True, corpus=None):
    # tipo: "count" (bolsa de palabras) o "tfidf"
    # corpus: lista de textos (ej. bloques) para ajustar el vocabulario/IDF.
    # Si es None, se ajusta solo con los 2 textos.
    clase = CountVectorizer if tipo == "count" else TfidfVectorizer
    try:
        vec = clase(
            preprocessor=normalizar,
            ngram_range=ngram,
            stop_words=list(STOP_ES) if quitar_stopwords else None,
        )
        vec.fit(corpus if corpus else [texto1, texto2])
        matriz = vec.transform([texto1, texto2])
        return float(cosine_similarity(matriz[0], matriz[1])[0][0])
    except ValueError:
        return 0.0


def dividir_en_bloques(texto, palabras_por_bloque):
    palabras = texto.split()
    return [
        " ".join(palabras[i:i + palabras_por_bloque])
        for i in range(0, len(palabras), palabras_por_bloque)
    ]