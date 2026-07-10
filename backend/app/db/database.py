from sqlalchemy import create_engine # import para crear una instancia de la clase Engine, que se utiliza para conectarse a la base de datos.
from sqlalchemy.orm import DeclarativeBase, sessionmaker 

from app.config import settings # importa la instancia de la clase Settings desde el archivo config.py, lo que permite acceder a las variables de entorno definidas en ese archivo.



engine = create_engine(settings.database_url) # Crea una instancia

SessionLocal = sessionmaker(
    autocommit=False, # no permite que se realicen cambios en la base de datos sin confirmarlos explícitamente.
    autoflush=False, # autoflush=False significa que los cambios realizados en la sesión no se enviarán automáticamente a la base de datos hasta que se llame explícitamente al método flush() o commit().
    bind=engine,
)

class Base(DeclarativeBase): 
    pass

def get_db():
    db = SessionLocal() # crea una nueva sesión de base de datos utilizando la clase SessionLocal.
    try: 
        yield db # yield devuelve la sesión de base de datos al llamador, lo que permite que se realicen operaciones en la base de datos.
    finally: 
        db.close() # cierra la sesión de base de datos después de que se hayan realizado todas las operaciones necesarias. Esto es importante para liberar recursos y evitar problemas de conexión a la base de datos.