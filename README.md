# ReviewMind AI

ReviewMind AI es una aplicación web full-stack para analizar reseñas de clientes, detectar patrones de sentimiento, identificar fortalezas y debilidades recurrentes, y generar informes ejecutivos para negocios.

El proyecto está planteado como una aplicación tipo SaaS y como proyecto portfolio, usando un stack moderno con FastAPI, PostgreSQL, SQLAlchemy, Alembic, Next.js, TypeScript y Tailwind CSS.

---

## Funcionalidades

- Crear y gestionar negocios.
- Añadir reseñas manualmente.
- Importar reseñas desde archivos CSV.
- Analizar sentimiento de reseñas.
- Detectar aspectos positivos y negativos recurrentes.
- Mostrar resumen de análisis por negocio.
- Visualizar gráficos de sentimiento y aspectos detectados.
- Generar informes ejecutivos.
- Guardar informes en PostgreSQL.
- Recuperar el último informe generado.
- Exportar informes a PDF.
- Integración opcional con OpenAI para informes generados por IA.
- Fallback automático a informes basados en reglas si OpenAI no está disponible.

---

## Stack técnico

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
- PostgreSQL en contenedor

---

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
├── .gitignore
└── README.md
```

---

## Requisitos previos

Antes de arrancar el proyecto necesitas tener instalado:

- Python 3.12 o superior
- Node.js 20 o superior
- Docker Desktop
- Git

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd reviewmind-ai
```

---

### 2. Levantar PostgreSQL con Docker

Desde la raíz del proyecto:

```bash
docker compose up -d
```

Esto levanta el contenedor de PostgreSQL definido en `docker-compose.yml`.

---

### 3. Configurar variables de entorno del backend

Crea un archivo `.env` dentro de la carpeta `backend/`.

Puedes usar como referencia el archivo:

```text
backend/.env.example
```

Contenido recomendado:

```env
DATABASE_URL=postgresql+psycopg://reviewmind_user:reviewmind_password@localhost:5432/reviewmind

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
ENABLE_AI_REPORTS=false
```

Por defecto, los informes se generan mediante reglas internas. Para activar OpenAI, añade una API key válida y cambia:

```env
ENABLE_AI_REPORTS=true
```

---

### 4. Instalar dependencias del backend

En Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En macOS/Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### 5. Aplicar migraciones de base de datos

Desde la carpeta `backend`, con el entorno virtual activo:

```bash
alembic upgrade head
```

Para comprobar la migración actual:

```bash
alembic current
```

---

### 6. Arrancar el backend

Desde `backend`:

```bash
fastapi dev app/main.py
```

La API estará disponible en:

```text
http://localhost:8000
```

La documentación Swagger estará disponible en:

```text
http://localhost:8000/docs
```

---

### 7. Configurar variables de entorno del frontend

Crea un archivo `.env.local` dentro de la carpeta `frontend/`.

Puedes usar como referencia:

```text
frontend/.env.local.example
```

Contenido:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 8. Instalar dependencias del frontend

En otra terminal:

```bash
cd frontend
npm install
```

---

### 9. Arrancar el frontend

Desde `frontend`:

```bash
npm run dev
```

La aplicación estará disponible en:

```text
http://localhost:3000
```

---

## Formato de importación CSV

Los archivos CSV deben incluir como mínimo una columna:

```text
text
```

Columnas opcionales:

```text
rating, author, source, language
```

Ejemplo:

```csv
text,rating,author,source,language
"El hotel estaba muy limpio y el personal fue muy amable",5,Ana,google,es
"La habitación era cómoda, pero había mucho ruido por la noche",3,Carlos,booking,es
"El servicio fue lento y el precio me pareció caro",2,Marta,tripadvisor,es
```

---

## Endpoints principales

### Businesses

```text
GET    /businesses
POST   /businesses
GET    /businesses/{business_id}
DELETE /businesses/{business_id}
```

### Reviews

```text
GET    /businesses/{business_id}/reviews
POST   /businesses/{business_id}/reviews
POST   /businesses/{business_id}/reviews/import-csv
DELETE /businesses/{business_id}/reviews/{review_id}
```

### Analysis

```text
POST /businesses/{business_id}/analysis/run
GET  /businesses/{business_id}/analysis
GET  /businesses/{business_id}/analysis/summary
```

### Reports

```text
POST /businesses/{business_id}/reports/generate
GET  /businesses/{business_id}/reports
GET  /businesses/{business_id}/reports/latest
GET  /businesses/{business_id}/reports/latest/pdf
```

---

## Informes con IA

ReviewMind AI puede generar informes ejecutivos de dos formas:

### 1. Informe basado en reglas

Es el modo por defecto.

```env
ENABLE_AI_REPORTS=false
```

Este modo no requiere API key y siempre está disponible.

### 2. Informe con OpenAI

Para activar informes con OpenAI:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
ENABLE_AI_REPORTS=true
```

Si la llamada a OpenAI falla por falta de créditos, error de conexión, clave inválida u otro problema, el backend usa automáticamente el generador basado en reglas como fallback.

---

## Migraciones con Alembic

El proyecto usa Alembic para gestionar cambios en la base de datos.

Crear una nueva migración después de modificar modelos SQLAlchemy:

```bash
alembic revision --autogenerate -m "describe change"
```

Aplicar migraciones:

```bash
alembic upgrade head
```

Comprobar migración actual:

```bash
alembic current
```

Revertir una migración:

```bash
alembic downgrade -1
```

---

## Comandos útiles

### Entrar en PostgreSQL

```bash
docker exec -it reviewmind-postgres psql -U reviewmind_user -d reviewmind
```

### Ver tablas

```sql
\dt
```

### Consultar negocios

```sql
SELECT id, name, category, location, created_at
FROM businesses
ORDER BY created_at DESC;
```

### Consultar reseñas

```sql
SELECT id, business_id, rating, author, text
FROM reviews
ORDER BY id DESC;
```

### Consultar informes

```sql
SELECT id, business_id, created_at
FROM reports
ORDER BY created_at DESC;
```

### Salir de PostgreSQL

```sql
\q
```

---

## Estado del proyecto

MVP completado.

El proyecto incluye:

- API REST con FastAPI.
- Persistencia con PostgreSQL.
- Modelado relacional con SQLAlchemy.
- Migraciones con Alembic.
- Importación de datos desde CSV.
- Análisis de reseñas.
- Dashboard frontend con Next.js.
- Visualización de métricas con gráficos.
- Generación y persistencia de informes.
- Exportación de informes a PDF.
- Integración preparada con OpenAI.

---

## Roadmap

Posibles mejoras futuras:

- Añadir autenticación de usuarios.
- Asociar negocios a usuarios.
- Añadir vista de histórico de informes.
- Añadir filtros por fecha, rating o fuente.
- Mejorar el análisis NLP con modelos multilingües.
- Añadir proveedor local de IA con Ollama.
- Dockerizar backend y frontend.
- Añadir tests automatizados.
- Desplegar la aplicación online.

---

## Autor

Proyecto desarrollado como aplicación full-stack de portfolio para demostrar competencias en backend, frontend, bases de datos, migraciones, procesamiento de datos, visualización e integración con IA.