from datetime import datetime

from pydantic import BaseModel, ConfigDict

# el archivo schemas define los esquemas de datos que se utilizan para validar y serializar la información que se envía y recibe a través de la API. 
# Estos esquemas se basan en las clases de modelos definidas en models.py, pero no contienen la lógica de la base de datos ni las relaciones entre tablas.

class BusinessBase(BaseModel): 
    name: str 
    category: str
    location: str | None = None 

class BusinessCreate(BusinessBase): # Esquema para crear un nuevo negocio
    pass 

class BusinessResponse(BusinessBase): 
    id: int 
    created_at: datetime

model_config = ConfigDict(from_attributes=True) # Configuración para que Pydantic pueda crear instancias de los esquemas a partir de los modelos de SQLAlchemy.
# Esto permite que los esquemas puedan ser utilizados para serializar y deserializar los datos de los modelos de la base de datos.