from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Barrio(SQLModel, table=True):
    __tablename__ = "barrios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    coordenadas_centroide: Optional[str] = Field(default=None, max_length=100)

    sensores: List["Sensor"] = Relationship(back_populates="barrio")


class Sensor(SQLModel, table=True):
    __tablename__ = "sensores"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_sensor: str = Field(max_length=50, unique=True)
    tipo: str = Field(max_length=50)
    unidad_medida: str = Field(max_length=20)
    barrio_id: int = Field(foreign_key="barrios.id")

    barrio: Optional[Barrio] = Relationship(back_populates="sensores")
    mediciones: List["Medicion"] = Relationship(back_populates="sensor")
    alertas: List["Alerta"] = Relationship(back_populates="sensor")


class Medicion(SQLModel, table=True):
    __tablename__ = "mediciones"

    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensores.id")
    valor: Decimal = Field(max_digits=10, decimal_places=2)
    fecha_registro: datetime = Field(default_factory=datetime.now)

    sensor: Optional[Sensor] = Relationship(back_populates="mediciones")


class Alerta(SQLModel, table=True):
    __tablename__ = "alertas"

    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensores.id")
    valor_disparado: Decimal = Field(max_digits=10, decimal_places=2)
    descripcion: str = Field(max_length=255)
    fecha_alerta: datetime = Field(default_factory=datetime.now)

    sensor: Optional[Sensor] = Relationship(back_populates="alertas")
