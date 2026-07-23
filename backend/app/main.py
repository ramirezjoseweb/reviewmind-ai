from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.models.business import Business
from app.models.review import Review
from app.routers import businesses, reviews

Base.metadata.create_all(bind=engine) # crea todas las tablas definidas en la clase Base en la base de datos, utilizando el motor de base de datos especificado en la variable engine. Esto asegura que todas las tablas necesarias estén presentes en la base de datos antes de que se realicen operaciones en ella.

app = FastAPI(
    title="ReviewMind API", 
    version="0.1.0",
    description="APIfor ReviewMind application",
) 

app.add_middleware(
        CORSMiddleware, # permite que la API sea accedida desde diferentes dominios, lo que es útil para aplicaciones web que se ejecutan en un navegador y necesitan acceder a la API desde un dominio diferente al de la API.
        allow_origins=[
            "http://localhost:3000", 
            "http://localhost:5173", 
            "http://localhost:8000",
        ], 
        allow_credentials=True, # permite que la API acepte solicitudes HTTP que incluyan credenciales (como cookies o encabezados de autenticación) desde los orígenes permitidos.
        allow_methods=["*"], # permite que la API acepte solicitudes HTTP de cualquier método (GET, POST, PUT, DELETE, etc.) desde los orígenes permitidos.
        allow_headers=["*"], # permite que la API acepte solicitudes HTTP con cualquier encabezado desde los orígenes permitidos.
)

app.include_router(businesses.router) # incluye el enrutador de negocios en la aplicación FastAPI, lo que permite que las rutas definidas en el enrutador estén disponibles en la API. Esto organiza las rutas relacionadas con los negocios en un solo lugar y facilita su mantenimiento y escalabilidad.
app.include_router(reviews.router)

@app.get("/")
def root(): 
    return{
        "message": "Welcome to ReviewMind API"
    }
    

@app.get("/health") 
def health_check(): 
    return{
        "status": "OK"
    }

#fastapi dev app/main.py || uvicorn app.main:app --reload
#docker compose up -d
#npm run dev

#lanzar postgressql
#docker exec -it reviewmind-postgres psql -U reviewmind_user -d reviewmind