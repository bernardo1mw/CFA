"""
Router para operações relacionadas a placas.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import cv2
import numpy as np
import base64
from datetime import datetime
import os

from ..models.placa import (
    PlacaResponse, 
    PlacaUpdate, 
    PlacaSearchRequest, 
    ImageUploadResponse
)
from ..services.database import db_service
from ..services.anpr_service import anpr_service

router = APIRouter(prefix="/api/placas", tags=["placas"])


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    image: UploadFile = File(...),
    image_base64: str = Form(None)
):
    """
    Upload de imagem para reconhecimento de placa.
    Suporta tanto upload de arquivo quanto imagem em base64 (captura de câmera).
    """
    try:
        # Processa imagem da câmera (base64)
        if image_base64:
            try:
                header, encoded = image_base64.split(",", 1)
                image_data = base64.b64decode(encoded)
                nparr = np.frombuffer(image_data, np.uint8)
                imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if imagem is None:
                    raise HTTPException(status_code=400, detail="Erro ao processar imagem da câmera")
                
                # Reconhece a placa
                texto_placa, imagem_resultado = anpr_service.reconhecer_placa_robusto(imagem)
                
                if not texto_placa or imagem_resultado is None:
                    raise HTTPException(status_code=400, detail="Não foi possível reconhecer uma placa na imagem")
                
                # Converte imagem resultado para base64
                _, buffer = cv2.imencode('.png', imagem_resultado)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Salva no banco de dados
                placa_data = {
                    'placa': texto_placa,
                    'filename': 'capturada_webcam.png',
                    'image_base64': img_base64,
                    'hora_entrada': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'hora_saida': None
                }
                
                placa_id = db_service.create_placa(placa_data)
                
                return ImageUploadResponse(
                    placa=texto_placa,
                    image_base64=img_base64,
                    success=True,
                    message="Placa reconhecida com sucesso"
                )
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro ao processar imagem da câmera: {str(e)}")
        
        # Processa upload de arquivo
        else:
            if not image:
                raise HTTPException(status_code=400, detail="Nenhuma imagem foi enviada")
            
            # Valida tipo de arquivo
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
            
            # Lê o arquivo
            contents = await image.read()
            nparr = np.frombuffer(contents, np.uint8)
            imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if imagem is None:
                raise HTTPException(status_code=400, detail="Erro ao processar a imagem enviada")
            
            # Reconhece a placa
            texto_placa, imagem_resultado = anpr_service.reconhecer_placa_robusto(imagem)
            
            if not texto_placa or imagem_resultado is None:
                raise HTTPException(status_code=400, detail="Não foi possível reconhecer uma placa na imagem")
            
            # Converte imagem resultado para base64
            _, buffer = cv2.imencode('.png', imagem_resultado)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Salva no banco de dados
            placa_data = {
                'placa': texto_placa,
                'filename': image.filename,
                'image_base64': img_base64,
                'hora_entrada': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hora_saida': None
            }
            
            placa_id = db_service.create_placa(placa_data)
            
            return ImageUploadResponse(
                placa=texto_placa,
                image_base64=img_base64,
                success=True,
                message="Placa reconhecida com sucesso"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")


@router.get("/", response_model=List[PlacaResponse])
async def get_all_placas(limit: int = 100):
    """
    Lista todas as placas registradas.
    """
    try:
        placas = db_service.get_all_placas(limit)
        return [PlacaResponse(**placa) for placa in placas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar placas: {str(e)}")


@router.get("/admin/test")
async def test_endpoint():
    """
    Endpoint de teste para verificar se o router está funcionando.
    """
    return {"message": "Router funcionando!", "status": "ok"}


@router.get("/admin/clean")
async def clean_invalid_records():
    """
    Remove registros inválidos (com placa nula) do banco de dados
    """
    try:
        deleted_count = db_service.clean_invalid_records()
        return {
            "message": f"Limpeza concluída. {deleted_count} registro(s) inválido(s) removido(s).",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar registros: {str(e)}")


@router.post("/search", response_model=PlacaResponse)
async def search_placa(search_request: PlacaSearchRequest):
    """
    Busca uma placa pelo número.
    """
    try:
        placa = db_service.get_placa_by_number(search_request.placa)
        if not placa:
            raise HTTPException(status_code=404, detail=f"A placa {search_request.placa} não foi encontrada no sistema")
        return PlacaResponse(**placa)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar placa: {str(e)}")


@router.get("/{placa_id}", response_model=PlacaResponse)
async def get_placa_by_id(placa_id: str):
    """
    Busca uma placa pelo ID.
    """
    try:
        placa = db_service.get_placa_by_id(placa_id)
        if not placa:
            raise HTTPException(status_code=404, detail="Placa não encontrada")
        return PlacaResponse(**placa)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar placa: {str(e)}")


@router.put("/{placa_id}", response_model=PlacaResponse)
async def update_placa(placa_id: str, update_data: PlacaUpdate):
    """
    Atualiza uma placa existente.
    """
    try:
        # Verifica se a placa existe
        placa_existente = db_service.get_placa_by_id(placa_id)
        if not placa_existente:
            raise HTTPException(status_code=404, detail="Placa não encontrada")
        
        # Prepara dados para atualização (remove campos None)
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
        
        # Atualiza no banco
        success = db_service.update_placa(placa_id, update_dict)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao atualizar placa")
        
        # Retorna a placa atualizada
        placa_atualizada = db_service.get_placa_by_id(placa_id)
        return PlacaResponse(**placa_atualizada)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar placa: {str(e)}")


@router.delete("/{placa_id}")
async def delete_placa(placa_id: str):
    """
    Deleta uma placa.
    """
    try:
        # Verifica se a placa existe
        placa_existente = db_service.get_placa_by_id(placa_id)
        if not placa_existente:
            raise HTTPException(status_code=404, detail="Placa não encontrada")
        
        # Deleta do banco
        success = db_service.delete_placa(placa_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao deletar placa")
        
        return {"message": "Registro excluído com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar placa: {str(e)}")
