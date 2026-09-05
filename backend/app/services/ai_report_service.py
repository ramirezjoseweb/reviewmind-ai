import json
from datetime import datetime

import requests
from openai import OpenAI

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
    if settings.ai_report_provider == "ollama":
        return generate_ollama_executive_report(
            business=business,
            reviews=reviews,
            analyses=analyses,
        )

    if settings.ai_report_provider == "openai":
        return generate_openai_executive_report(
            business=business,
            reviews=reviews,
            analyses=analyses,
        )

    raise ValueError(f"Unsupported AI report provider: {settings.ai_report_provider}")


def generate_openai_executive_report(
    business: Business,
    reviews: list[Review],
    analyses: list[ReviewAnalysis],
) -> ExecutiveReportDraft:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

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
                "content": get_system_prompt(),
            },
            {
                "role": "user",
                "content": build_user_prompt(payload),
            },
        ],
    )

    parsed_report = parse_ai_report(response.output_text)

    return build_draft_from_parsed_report(
        business=business,
        parsed_report=parsed_report,
    )


def generate_ollama_executive_report(
    business: Business,
    reviews: list[Review],
    analyses: list[ReviewAnalysis],
) -> ExecutiveReportDraft:
    payload = build_report_payload(
        business=business,
        reviews=reviews,
        analyses=analyses,
    )

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"

    response = requests.post(
        url,
        json={
            "model": settings.ollama_model,
            "system": get_system_prompt(),
            "prompt": build_user_prompt(payload),
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()
    raw_text = data.get("response", "")

    parsed_report = parse_ai_report(raw_text)

    return build_draft_from_parsed_report(
        business=business,
        parsed_report=parsed_report,
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
        ) / len(analyses)
    else:
        average_sentiment_score = 0

    review_samples = [
        {
            "text": review.text,
            "rating": review.rating,
            "author": review.author,
            "source": review.source,
            "language": review.language,
        }
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
            "neutral_reviews": neutral_reviews,
            "negative_reviews": negative_reviews,
            "average_sentiment_score": round(average_sentiment_score, 2),
        },
        "review_samples": review_samples,
        "analysis_samples": analysis_samples,
    }


def get_system_prompt() -> str:
    return (
        "Eres un analista experto en experiencia de cliente. "
        "Generas informes ejecutivos claros, breves y accionables "
        "a partir de reseñas y análisis de sentimiento. "
        "Responde siempre en JSON válido, sin markdown, sin texto adicional."
    )


def build_user_prompt(payload: dict) -> str:
    return (
        "Genera un informe ejecutivo para este negocio. "
        "Devuelve únicamente un JSON con estas claves exactas: "
        "executive_summary, sentiment_overview, strengths, weaknesses, "
        "recommendations, priority_actions. "
        "Las claves strengths, weaknesses, recommendations y priority_actions "
        "deben ser listas de strings. "
        "Escribe todo en español profesional, claro y directo. "
        f"Datos:\n{json.dumps(payload, ensure_ascii=False, default=str)}"
    )


def parse_ai_report(raw_text: str) -> dict:
    cleaned_text = raw_text.strip()

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError:
        start = cleaned_text.find("{")
        end = cleaned_text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("AI response was not valid JSON")

        parsed = json.loads(cleaned_text[start : end + 1])

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
            raise ValueError(f"AI response missing key: {key}")

    for key in [
        "strengths",
        "weaknesses",
        "recommendations",
        "priority_actions",
    ]:
        if not isinstance(parsed[key], list):
            raise ValueError(f"AI response key must be a list: {key}")

        parsed[key] = [str(item) for item in parsed[key]]

    parsed["executive_summary"] = str(parsed["executive_summary"])
    parsed["sentiment_overview"] = str(parsed["sentiment_overview"])

    return parsed


def build_draft_from_parsed_report(
    business: Business,
    parsed_report: dict,
) -> ExecutiveReportDraft:
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