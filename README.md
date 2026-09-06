# ReviewMind AI

ReviewMind AI is a web application for analyzing customer reviews, detecting sentiment patterns, identifying recurring strengths and weaknesses, and generating executive reports for businesses.

The project was built as a full-stack portfolio application using FastAPI, PostgreSQL, SQLAlchemy, Alembic, Next.js, TypeScript and Tailwind CSS.

## Features

- Create and manage businesses.
- Add customer reviews manually.
- Import reviews from CSV files.
- Analyze review sentiment.
- Detect positive and negative aspects.
- Display sentiment summaries and dashboard charts.
- Generate executive business reports.
- Store generated reports in PostgreSQL.
- Export reports to PDF.
- Optional OpenAI-based report generation with fallback to rule-based reports.

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Pandas
- ReportLab
- OpenAI SDK

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Recharts

### Infrastructure

- Docker
- Docker Compose
- PostgreSQL container

## Project Structure

```text
reviewmind-ai/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   └── main.py
│   ├── migrations/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── .env.local.example
├── docker-compose.yml
└── README.md

# ReviewMind AI

ReviewMind AI es una aplicación web para analizar reseñas de clientes, detectar patrones de sentimiento, identificar fortalezas y debilidades recurrentes, y generar informes ejecutivos para negocios.

El proyecto se ha construido como una aplicación full-stack de portfolio usando FastAPI, PostgreSQL, SQLAlchemy, Alembic, Next.js, TypeScript y Tailwind CSS.

## Funcionalidades

- Crear y gestionar negocios.
- Añadir reseñas de clientes manualmente.
- Importar reseñas desde archivos CSV.
- Analizar el sentimiento de las reseñas.
- Detectar aspectos positivos y negativos.
- Mostrar resúmenes de sentimiento y gráficos en un dashboard.
- Generar informes ejecutivos para negocios.
- Guardar los informes generados en PostgreSQL.
- Exportar informes a PDF.
- Generación opcional de informes con OpenAI, con fallback a informes basados en reglas.

## Stack tecnológico

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Pandas
- ReportLab
- OpenAI SDK

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Recharts

### Infraestructura

- Docker
- Docker Compose
- Contenedor de PostgreSQL

## Estructura del proyecto

```text
reviewmind-ai/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   └── main.py
│   ├── migrations/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── .env.local.example
├── docker-compose.yml
└── README.md