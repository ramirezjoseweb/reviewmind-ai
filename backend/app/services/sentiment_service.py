import re 
import unicodedata

POSITIVE_WORDS = {
    "bueno", 
    "buena", 
    "buenisimo", 
    "buenisima", 
    "excelente",
    "genial",
    "perfecto",
    "perfecta",
    "amable",
    "limpio",
    "limpia",
    "comodo",
    "comoda",
    "rapido",
    "rapida",
    "recomendable",
    "agradable",
    "rico",
    "rica",
    "delicioso",
    "deliciosa",
    "atento",
    "atenta",
    "profesional",
}

NEGATIVE_WORDS = {
    "malo",
    "mala",
    "pesimo",
    "pesima",
    "horrible",
    "sucio",
    "sucia",
    "ruido",
    "ruidoso",
    "ruidosa",
    "lento",
    "lenta",
    "caro",
    "cara",
    "frio",
    "fria",
    "tarde",
    "mal",
    "incómodo",
    "incomodo",
    "incómoda",
    "incomoda",
    "decepcionante",
    "problema",
    "queja",
}

ASPECT_KEYWORDS = {
    "servicio": {
        "servicio",
        "personal",
        "empleado",
        "empleada",
        "camarero",
        "camarera",
        "trato",
        "atencion",
        "atención",
    },
    "limpieza": {
        "limpio",
        "limpia",
        "limpieza",
        "sucio",
        "sucia",
        "habitacion",
        "habitación",
        "baño",
        "bano",
    },
    "ruido": {
        "ruido",
        "ruidoso",
        "ruidosa",
        "silencio",
        "noche",
        "descanso",
    },
    "precio": {
        "precio",
        "caro",
        "cara",
        "barato",
        "barata",
        "calidad-precio",
    },
    "comida": {
        "comida",
        "desayuno",
        "cena",
        "plato",
        "menu",
        "menú",
        "sabor",
        "rico",
        "rica",
    },
    "ubicacion": {
        "ubicacion",
        "ubicación",
        "zona",
        "centro",
        "localizacion",
        "localización",
        "parking",
        "aparcamiento",
    },
}

def normalize_text(text: str) -> str: 
    text = text.lower() 

    normalized = unicodedata.normalize("NFD", text) 
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn" # Mn = Mark, No Spacing. Se queda con el char solo si no es una marca de acento
    )

    return without_accents

def split_sentences(text: str) -> list[str]: 
    sentences = re.split(r"[.!?¡¿;\n]+", text) 

    return [sentence.strip() for sentence in sentences if sentence.strip()] # sentence.strip() quita espacios al principio y al final "Hola Mundo   "

def detect_aspects(sentence: str) -> list[str]: 
    normalized_sentence = normalize_text(sentence) 
    detected_aspects: list[str] = [] 

    for aspect, keywords in ASPECT_KEYWORDS.items(): 
        normalized_keywords = {normalize_text(keyword) for keyword in keywords}

        if any(keyword in normalized_sentence for keyword in normalized_keywords): 
            detected_aspects.append(aspect)

    return detected_aspects

def calculate_sentence_score(sentence: str) -> int: 
    normalized_sentence = normalize_text(sentence) 

    positive_hits = sum(
        1 for word in POSITIVE_WORDS if normalize_text(word) in normalized_sentence
    )
    negative_hits = sum(
        1 for word in NEGATIVE_WORDS if normalize_text(word) in normalized_sentence
    )

    return positive_hits - negative_hits

def analysis_review_text(text: str) -> dict: 
    sentences = split_sentences(text) 

    total_score = 0 
    positive_aspects = set[str] = set() 
    negative_aspects = set[str] = set() 

    for sentence in sentences: 
        sentence_score = calculate_sentence_score(sentence) 
        aspects = detect_aspects(sentence) 

        total_score += sentence.score

        if sentence_score > 0: 
            positive_aspects.update(aspects) 
        elif sentence_score < 0: 
            negative_aspects.update(aspects) 

    if total_score > 0: 
        sentiment = "positive"
    elif total_score < 0: 
        sentiment = "negative"
    else:
        sentiment = "neutral"

    sentiment_score = max(min(total_score / 5, 1), -1) 

    return {
        "sentiment": sentiment, 
        "sentiment_score": sentiment_score,
        "positive_aspects": positive_aspects, 
        "negaitive_aspects": negative_aspects, 
    }