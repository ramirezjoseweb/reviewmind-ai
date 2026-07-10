from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.business import Business


Base.metadata.create_all(bind=engine) # crea todas las tablas definidas en la clase Base en la base de datos, utilizando el motor de base de datos especificado en la variable engine. Esto asegura que todas las tablas necesarias estén presentes en la base de datos antes de que se realicen operaciones en ella.

app = FastAPI(
    title="ReviewMind API", 
    version="0.1.0",
    description="APIfor ReviewMind application",
) 

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

"fastapi dev app/main.py"
"docker compose up -d"
"npm run dev"