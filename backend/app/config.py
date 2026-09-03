from pydantic_settings import BaseSettings # import para configurar variables de entorno

class Settings(BaseSettings): # la clase Settings hereda de BaseSettings, lo que permite definir variables de entorno y sus valores predeterminados.
    database_url: str
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    enable_ai_reports: bool = False

    class Config: # class Config es una clase interna que se utiliza para configurar la clase Settings.
        env_file = ".env" 

settings = Settings() 