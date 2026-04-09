from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Configuración de la Base de Datos (SQLite)
DATABASE_URL = "sqlite:///./database/agenda.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Definición de la tabla de Citas
class Cita(Base):
    __tablename__ = "citas"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_nombre = Column(String, nullable=True)
    fecha = Column(String)  # Guardaremos "2026-03-30"
    hora = Column(String)   # Guardaremos "10:00"
    motivo = Column(String)
    estado = Column(String, default="programada")

# 3. Crear el archivo físico de la base de datos
Base.metadata.create_all(bind=engine)