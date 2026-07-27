import re 
import unicodedata

POSITIVE_WORDS = {
    "accesible",
    "acogedor",
    "acogedora",
    "agradable",
    "amable",
    "amplio",
    "amplia",
    "atento",
    "atenta",
    "barato",
    "barata",
    "bien",
    "buen",
    "buena",
    "buenas vistas",
    "bueno",
    "buenisima",
    "buenisimo",
    "calidad",
    "centrico",
    "centrica",
    "comodo",
    "comoda",
    "correcto",
    "correcta",
    "deliciosa",
    "delicioso",
    "encanta",
    "encantado",
    "encantadora",
    "encantador",
    "excelente",
    "excepcional",
    "fantastica",
    "fantastico",
    "genial",
    "impecable",
    "increible",
    "limpia",
    "limpio",
    "maravillosa",
    "maravilloso",
    "perfecta",
    "perfecto",
    "profesional",
    "rapida",
    "rapido",
    "recomendable",
    "repetiria",
    "rica",
    "rico",
    "satisfecho",
    "satisfecha",
    "silenciosa",
    "silencioso",
    "tranquila",
    "tranquilo",
    "volveria",
    "volveremos",
}

NEGATIVE_WORDS = {
    "aburrido",
    "aburrida",
    "agobiante",
    "calor",
    "caluroso",
    "cara",
    "caro",
    "decepcion",
    "decepcionado",
    "decepcionada",
    "decepcionante",
    "deficiente",
    "desagradable",
    "desastre",
    "disgustado",
    "disgustada",
    "fatal",
    "fria",
    "frio",
    "horrible",
    "humedad",
    "incomoda",
    "incomodo",
    "lenta",
    "lento",
    "mal",
    "mala",
    "malo",
    "mejorable",
    "no me ha gustado",
    "no volveria",
    "pesima",
    "pesimo",
    "problema",
    "queja",
    "regular",
    "ruido",
    "ruidosa",
    "ruidoso",
    "sucia",
    "sucio",
    "tarde",
}

ASPECT_KEYWORDS = {
    "ambiente": {
        "ambiente",
        "decoracion",
        "entorno",
        "musica",
        "terraza",
        "tranquilidad",
        "vistas",
    },

    "comida": {
        "bebida",
        "cafe",
        "carta",
        "cena",
        "comida",
        "desayuno",
        "menu",
        "plato",
        "racion",
        "sabor",
    },

    "habitacion": {
        "almohada",
        "cama",
        "habitacion",
        "sabana",
        "toalla",
    },

    "instalaciones": {
        "ascensor",
        "ducha",
        "gimnasio",
        "instalaciones",
        "piscina",
        "recepcion",
        "terraza",
    },

    "limpieza": {
        "bano",
        "habitacion",
        "limpia",
        "limpieza",
        "limpio",
        "olores",
        "sucia",
        "sucio",
    },

    "opiniones": {
        "gustado",
        "me encanta",
        "me ha encantado",
        "no me ha gustado",
        "recomendable",
        "volveria",
        "volveremos",
    },

    "precio": {
        "barata",
        "barato",
        "calidad-precio",
        "cara",
        "caro",
        "coste",
        "precio",
        "tarifa",
    },

    "ruido": {
        "descanso",
        "noche",
        "ruido",
        "ruidosa",
        "ruidoso",
        "silencio",
        "silenciosa",
        "silencioso",
    },

    "servicio": {
        "amabilidad",
        "atencion",
        "camarera",
        "camarero",
        "empleada",
        "empleado",
        "personal",
        "recepcionista",
        "servicio",
        "trato",
    },

    "ubicacion": {
        "aparcamiento",
        "centrico",
        "centrica",
        "centro",
        "localizacion",
        "parking",
        "ubicacion",
        "zona",
    },

    "wifi": {
        "conexion",
        "internet",
        "senal",
        "wifi",
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

def analyze_review_text(text: str) -> dict: 
    sentences = split_sentences(text) 

    total_score = 0 
    positive_aspects:  set[str] = set() 
    negative_aspects: set[str] = set() 

    for sentence in sentences: 
        sentence_score = calculate_sentence_score(sentence) 
        aspects = detect_aspects(sentence) 

        total_score += sentence_score

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
        "positive_aspects": sorted(positive_aspects), 
        "negative_aspects": sorted(negative_aspects), 
    }