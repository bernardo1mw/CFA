"""
Modelos Pydantic para o sistema de reconhecimento de placas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PlacaBase(BaseModel):
    """Modelo base para placa."""
    placa: Optional[str] = Field(None, description="Número da placa do veículo")
    filename: Optional[str] = Field(None, description="Nome do arquivo da imagem")
    image_base64: Optional[str] = Field(None, description="Imagem em base64")
    hora_entrada: Optional[str] = Field(None, description="Horário de entrada")
    hora_saida: Optional[str] = Field(None, description="Horário de saída")


class PlacaCreate(BaseModel):
    """Modelo para criação de nova placa."""
    placa: str = Field(..., description="Número da placa do veículo")
    filename: str = Field(..., description="Nome do arquivo da imagem")
    image_base64: str = Field(..., description="Imagem em base64")
    hora_entrada: str = Field(..., description="Horário de entrada")
    hora_saida: Optional[str] = Field(None, description="Horário de saída")


class PlacaUpdate(BaseModel):
    """Modelo para atualização de placa."""
    placa: Optional[str] = None
    hora_entrada: Optional[str] = None
    hora_saida: Optional[str] = None


class PlacaResponse(PlacaBase):
    """Modelo de resposta da placa."""
    id: str = Field(..., alias="_id", description="ID único do registro")
    
    class Config:
        populate_by_name = True


class PlacaSearchRequest(BaseModel):
    """Modelo para busca de placa."""
    placa: str = Field(..., description="Número da placa para buscar")


class ImageUploadResponse(BaseModel):
    """Modelo de resposta para upload de imagem."""
    id: Optional[str] = Field(None, alias="_id", description="ID único do registro")
    placa: str = Field(..., description="Placa reconhecida")
    image_base64: str = Field(..., description="Imagem processada em base64")
    success: bool = Field(True, description="Indica se o processamento foi bem-sucedido")
    message: Optional[str] = Field(None, description="Mensagem adicional")
    image_url: Optional[str] = Field(None, description="URL para acessar a imagem original")

    class Config:
        populate_by_name = True
