from datetime import datetime
from collections import Counter

from app.schemas.report import ExecutiveReportDraft

from app.models.business import Business
from app.models.review import Review
from app.models.review_analysis import ReviewAnalysis

RECOMMENDATION_BY_ASPECT = {
    "servicio": "Revisar la calidad del servicio, tiempos de respuesta y trato del personal.",
    "limpieza": "Refuerza los controles de limpieza y revisiones periódicas.",
    "ruido": "Identifica las fuentes de ruido y plantea medidas de aislamiento o gestión de horarios.",
    "precio": "Revisa la percepción de valor: comunica mejor beneficios o ajusta la propuesta calidad-precio.",
    "comida": "Analiza los comentarios sobre comida para mejorar platos, tiempos y consistencia.",
    "ubicacion": "Mejora la información sobre acceso, aparcamiento, transporte o puntos cercanos.",
    "habitacion": "Revisa el estado, comodidad y mantenimiento de habitaciones o espacios equivalentes.",
    "opiniones": "Agrupa opiniones recurrentes para detectar patrones de mejora.",
}

def generate_executive_report(
    business: Business, 
    reviews: list[Review], 
    analyses: list[ReviewAnalysis], 
) -> ExecutiveReportDraft: 
    total_reviews = len(reviews) 
    analyzed_reviews = len(analyses)

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
        average_score = sum(
            analysis.sentiment_score for analysis in analyses
        ) / analyzed_reviews
    else: 
        average_score = 0 

    positive_counter: Counter[str] = Counter() 
    negative_counter: Counter[str] = Counter() 

    for analysis in analyses: 
        positive_counter.update(analysis.positive_aspects)
        negative_counter.update(analysis.negative_aspects)

    top_positive = positive_counter.most_common(5)
    top_negative = negative_counter.most_common(5)

    if average_score > 0.25: 
        sentiment_label = "positivo"
    elif average_score < -0.25: 
        sentiment_label = "negativo"
    else: 
        sentiment_label = "neutral"

    executive_summary = (
        f"{business.name} cuenta con {total_reviews} reseñas registradas, "
        f"de las cuales {analyzed_reviews} han sido analizadas. "
        f"El sentimiento general detectado es {sentiment_label}, con "
        f"{positive_reviews} reseñas positivas, {neutral_reviews} reseñas neutrales y {negative_reviews} reseñas negaticas."
    )

    sentiment_overview = (
        f"La puntuación media de sentimiento es {round(average_score, 2)} "
        f"en una escala aproximada de -1 a 1. "
        f"Esto sugiere una percepción general {sentiment_label} por parte de los clientes"
    )

    strengths = [
        f"El aspecto '{aspect}' aparece como fortaleza en {count} reseñas."
        for aspect, count in top_positive
    ]

    weaknesses = [
        f"El aspecto '{aspect}' aparece como problema en {count} reseñas."
        for aspect, count in top_negative
    ]

    if not strengths: 
        strengths = [
            "No se han detectado fortalezas claras todavía."
        ]   

    if not weaknesses: 
        weaknesses = [
            "No se han detectado debilidades claras todavía." 
        ]

    recommendations = []

    for aspect, _ in top_negative: 
        recommendation = RECOMMENDATION_BY_ASPECT.get(
            aspect, 
            f"Revisar el aspecto '{aspect}' porque aparece de forma recurrente en comentarios negativos", 
        )
        recommendations.append(recommendation) 

    if not recommendations: 
        "Mantener la calidad actual y seguir recopilando reseñas para detectar recomendaciones."

    priority_actions = build_priority_actions(
        negative_reviews = negative_reviews, 
        positive_reviews = positive_reviews, 
        top_negative=top_negative,  
    )
    
    return ExecutiveReportDraft(
        business_id=business.id, 
        business_name=business.name,
        generated_at=datetime.utcnow(),
        executive_summary=executive_summary,
        sentiment_overview=sentiment_overview,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        priority_actions=priority_actions,
    )

def build_priority_actions(
        negative_reviews, 
        positive_reviews, 
        top_negative: list[tuple[str, int]], 
) -> list[str]: 
    actions: list[str] = []

    if negative_reviews > positive_reviews: 
        actions.append(
            "Priorizar la reducción de reseñas negativas antes de escalar acciones comerciales"
        )
    else:
        actions.append(
            "Mantener las fortalezas actuales y trabajar sobre los problemas más repetidos"
        )

    if top_negative: 
        main_problem, count = top_negative[0]
        actions.append(
            f"La mayor debilidad es el aspecto {main_problem}, ya que es el problema encontrado más frecuente con {count} menciones."
        )

    actions.append(
        "Revisar nuevas reseñas semanalmente para comprobar si las mejoras reducen los comentarios negativos."
    )

    return actions

