from fastapi import FastAPI

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