from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime

from app.db.database import Base # importa la clase Base desde el archivo database.py, lo que permite que la clase Business herede de ella y se convierta en una tabla de la base de datos.

from app.models.review import Review

class Business(Base): 
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # Mapped es un tipo de columna que se utiliza para mapear una columna de la base de datos a un atributo de la clase. En este caso, se está mapeando la columna id de la tabla businesses a un atributo id de la clase Business. El parámetro primary_key=True indica que esta columna es la clave primaria de la tabla, y el parámetro index=True indica que se debe crear un índice en esta columna para mejorar el rendimiento de las consultas.
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False, 
        )
    
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="business", 
        cascade="all, delete-orphan", # esto significa que si se elimina un negocio, todas las reseñas asociadas a ese negocio también se eliminarán automáticamente. La opción delete-orphan indica que si una reseña ya no está asociada a ningún negocio, también se eliminará automáticamente de la base de datos.
    )