import json 

from openai import OpenAI
from datetime import datetime

from app.config import settings
from app.models.business import Business
from app.models.review import Review
from app.models.review_analysis import ReviewAnalysis

from app.schemas.report import ExecutiveReportDraft

def generate_ai_executive_report(
        business: Business, 
        reviews: list[Review], 
        analyses: list[ReviewAnalysis], 
) -> ExecutiveReportDraft: 
    if not settings.openai_api_key: 
        raise ValueError("OPEN_API_KEY no está configurada") 

    client = OpenAI(api_key=settings.openai_api_key) 

    payload = build_report_payload(
        business=business, 
        reviews=reviews, 
        analyses=analyses,
    )

    response = client.responses.create(
        model=settings.openai_model, 
        input=[
            {
                "role": "system", 
                "content": (
                    "Eres un analista experto en experiencia de cliente. "
                    "Generas informes ejecutivos claros, breves y accionables "
                    "a partir de reseñas y análisis de sentimiento. "
                    "Responde siempre en JSON válido, sin markdown."
                ),
            },
            {
                "role": "user", 
                "content": (
                    "Genera un informe ejecutivo para este negocio. "
                    "Devuelve únicamente un JSON con estas claves exactas: "
                    "executive_summary, sentiment_overview, strengths, "
                    "weaknesses, recommendations, priority_actions. "
                    "Las claves strengths, weaknesses, recommendations y "
                    "priority_actions deben ser listas de strings. "
                    # Convierte los datos del informe a JSON legible y los agrega al mensaje.
                    f"Datos:\n{json.dumps(payload, ensure_ascii=False)}"
                ),
            },
        ],
    )

    raw_text = response.output_text
    parsed_report = parse_ai_report(raw_text) 

    return ExecutiveReportDraft(
        business_id=business.id, 
        business_name=business.name,
        generated_at=datetime.utcnow(), 
        executive_summary=parsed_report["executive_summary"],
        sentiment_overview=parsed_report["sentiment_overview"],
        strengths=parsed_report["strengths"],
        weaknesses=parsed_report["weaknesses"],
        recommendations=parsed_report["recommendations"],
        priority_actions=parsed_report["priority_actions"],
    )

def build_report_payload(
        business: Business, 
        reviews: list[Review], 
        analyses: list[ReviewAnalysis], 
) -> dict: 
    positive_reviews = sum(
        1 for analysis in analyses if analysis.sentiment == "positive"
    )
    neutral_reviews = sum(
        1 for analysis in analyses if analysis.sentiment == "neutral"
    )
    negative_reviews = sum(
        1 for analysis in analyses if analysis.sentiment == "negative"
    )

    if analyses: 
        average_sentiment_score = sum(
            analysis.sentiment_score for analysis in analyses
        ) /len(analyses)
    else: 
        average_sentiment_score = 0

    review_samples =  [
        {
            "text": review.text, 
            "rating": review.rating, 
            "author": review.author, 
            "source": review.source, 
            "language": review.language, 
        }
        # Recorre únicamente las primeras 20 reseñas para crear muestras del informe.
        for review in reviews[:20]
    ]

    analysis_samples = [
        {
            "sentiment": analysis.sentiment, 
            "sentiment_score": analysis.sentiment_score, 
            "positive_aspects": analysis.positive_aspects, 
            "negative_aspects": analysis.negative_aspects,
        }
        for analysis in analyses[:20]
    ]

    return {
        "generated_at": datetime.utcnow().isoformat(),        
        "business": {
            "id": business.id, 
            "name": business.name, 
            "category": business.category, 
            "location": business.location, 
        }, 
        "summary": {
            "total_reviews": len(reviews), 
            "analyzed_reviews": len(analyses), 
            "positive_reviews": positive_reviews, 
            "negative_reviews": negative_reviews, 
            "neutral_reviews": neutral_reviews, 
            "average_sentiment_score": round(average_sentiment_score, 2), 
        }, 
        "review_samples": review_samples, 
        "analysis_samples": analysis_samples, 
    }

def parse_ai_report(raw_text: str) -> dict: 
    try:
        # Convierte el texto JSON de la IA en un diccionario de Python.
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as error: 
        raise ValueError("La respuesta IA no es un JSON válido") from error

    required_keys = [
        "executive_summary", 
        "sentiment_overview", 
        "strengths", 
        "weaknesses", 
        "recommendations", 
        "priority_actions", 
    ]

    for key in required_keys: 
        if key not in parsed: 
            raise ValueError(f"Key faltante en respuesta IA: {key}")

        # Normaliza los campos listados para que cada elemento sea una cadena.
        # Esto evita errores si la IA devuelve números, booleanos u otros tipos.
        parsed[key] = [str(item) for item in parsed[key]]

    parsed["executive_summary"] = str(parsed["executive_summary"]) 
    parsed["sentiment_overview"] = str(parsed["sentiment_overview"])  

    return parsed
    