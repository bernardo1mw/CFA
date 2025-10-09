# -*- coding: utf-8 -*-
"""
Sistema AVANÇADO de OCR para reconhecimento de placas de veículos usando FastALPR.
Versão otimizada com detecção especializada e OCR de alta performance.
"""

import cv2
import numpy as np
import re
from typing import Tuple, Optional
import logging

from .alpr import ALPR, ALPRResult

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ANPRService:
    """Serviço para reconhecimento automático de placas usando FastALPR."""
    
    def __init__(self):
        """Inicializa o serviço ANPR com FastALPR."""
        try:
            logger.info("Inicializando FastALPR...")
            # Inicializa o sistema ALPR com configurações otimizadas
            self.alpr = ALPR(
                detector_model="yolo-v9-t-384-license-plate-end2end",
                detector_conf_thresh=0.4,
                ocr_model="cct-xs-v1-global-model",
                ocr_device="auto",  # Usa GPU se disponível, senão CPU
                ocr_force_download=False  # Usa cache se disponível
            )
            logger.info("FastALPR inicializado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao inicializar FastALPR: {e}")
            self.alpr = None

    def corrigir_caracteres_similares(self, texto: str) -> str:
        """
        Corrige caracteres frequentemente confundidos pelo OCR em placas.
        Mantido para compatibilidade, mas FastALPR já tem correções internas.
        
        Args:
            texto: Texto da placa reconhecida
            
        Returns:
            str: Texto corrigido
        """
        if not texto:
            return texto
            
        # Mapeamento de correções comuns em placas brasileiras
        correcoes = {
            'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'G': '6', 'B': '8'
        }
        
        texto_corrigido = ""
        for i, char in enumerate(texto):
            if len(texto) == 7:  # Placas brasileiras têm 7 caracteres
                if i < 3:  # Primeiras 3 posições são letras
                    if char.isdigit():
                        inv_map = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '6': 'G', '8': 'B'}
                        char = inv_map.get(char, char)
                elif i == 3 or i >= 5:  # Posições de números
                    if char.isalpha():
                        char = correcoes.get(char, char)
            
            texto_corrigido += char
        
        return texto_corrigido

    def filtrar_texto_placa(self, texto_bruto: str) -> Optional[str]:
        """
        Filtra o texto bruto reconhecido para extrair a sequência da placa.
        Mantido para compatibilidade, mas FastALPR já filtra automaticamente.
        """
        if not texto_bruto:
            return None
            
        texto_limpo = "".join(texto_bruto.split()).upper()
        
        # Padrão Mercosul (AAA1B23)
        match_mercosul = re.search(r'[A-Z]{3}[0-9][A-Z][0-9]{2}', texto_limpo)
        if match_mercosul:
            return self.corrigir_caracteres_similares(match_mercosul.group(0))
        
        # Padrão antigo (AAA1234)
        texto_sem_hifen = texto_limpo.replace('-', '')
        match_antigo = re.search(r'[A-Z]{3}[0-9]{4}', texto_sem_hifen)
        if match_antigo:
            return self.corrigir_caracteres_similares(match_antigo.group(0))
        
        # Padrão antigo com hífen (AAA-1234)
        match_antigo_hifen = re.search(r'[A-Z]{3}-[0-9]{4}', texto_limpo)
        if match_antigo_hifen:
            return match_antigo_hifen.group(0)
            
        # Fallback genérico
        match_generico = re.search(r'[A-Z0-9]{7}', texto_limpo)
        if match_generico and len(texto_limpo) < 15:
            return self.corrigir_caracteres_similares(match_generico.group(0))

        return None

    def formatar_placa(self, texto_placa: str) -> str:
        """
        Formata a placa de acordo com o padrão brasileiro.
        
        Args:
            texto_placa: Texto da placa sem formatação
            
        Returns:
            str: Placa formatada
        """
        if not texto_placa:
            return texto_placa
            
        # Remove espaços e converte para maiúsculo
        texto_limpo = "".join(texto_placa.split()).upper()
        
        # Se já tem hífen, retorna como está
        if '-' in texto_limpo:
            return texto_limpo
            
        # Se tem 7 caracteres e parece ser placa antiga (AAA1234)
        if len(texto_limpo) == 7 and texto_limpo[3].isdigit() and texto_limpo[0:3].isalpha() and texto_limpo[4:].isdigit():
            return f"{texto_limpo[0:3]}-{texto_limpo[3:]}"
        
        # Para placas Mercosul (AAA1B23), retorna sem hífen
        return texto_limpo

    def reconhecer_placa_robusto(self, imagem: np.ndarray) -> Tuple[Optional[str], Optional[np.ndarray]]:
        """
        Pipeline robusto para reconhecimento de placas usando FastALPR.
        
        Args:
            imagem: Imagem de entrada (numpy array)
            
        Returns:
            tuple: (texto_placa, imagem_resultado)
        """
        if self.alpr is None:
            logger.error("FastALPR não inicializado.")
            return None, None
        
        try:
            logger.info("Processando imagem com FastALPR...")
            
            # Usa FastALPR para detectar e reconhecer placas
            alpr_results = self.alpr.predict(imagem)
            
            if not alpr_results:
                logger.info("Nenhuma placa detectada.")
                return None, imagem
            
            # Pega o resultado com maior confiança
            melhor_resultado = max(alpr_results, key=lambda x: x.ocr.confidence if x.ocr else 0)
            
            if melhor_resultado.ocr is None or not melhor_resultado.ocr.text:
                logger.info("Placa detectada mas texto não reconhecido.")
                return None, imagem
            
            # Extrai o texto da placa
            texto_placa = melhor_resultado.ocr.text.strip()
            
            # Aplica filtros e correções se necessário
            texto_filtrado = self.filtrar_texto_placa(texto_placa)
            if texto_filtrado:
                texto_placa = texto_filtrado
            
            # Formata a placa
            texto_placa_formatado = self.formatar_placa(texto_placa)
            
            logger.info(f"Placa reconhecida: {texto_placa_formatado} (confiança: {melhor_resultado.ocr.confidence:.2f})")
            
            # Gera imagem com anotações
            imagem_resultado = self.alpr.draw_predictions(imagem)
            
            return texto_placa_formatado, imagem_resultado
            
        except Exception as e:
            logger.error(f"Erro durante reconhecimento: {e}")
            return None, imagem

    def reconhecer_multiplas_placas(self, imagem: np.ndarray) -> list[dict]:
        """
        Reconhece múltiplas placas na imagem (funcionalidade adicional do FastALPR).
        
        Args:
            imagem: Imagem de entrada (numpy array)
            
        Returns:
            list: Lista de dicionários com informações das placas detectadas
        """
        if self.alpr is None:
            return []
        
        try:
            alpr_results = self.alpr.predict(imagem)
            placas = []
            
            for result in alpr_results:
                if result.ocr and result.ocr.text:
                    placa_info = {
                        'texto': self.formatar_placa(result.ocr.text),
                        'confianca': result.ocr.confidence,
                        'bbox': {
                            'x1': result.detection.bounding_box.x1,
                            'y1': result.detection.bounding_box.y1,
                            'x2': result.detection.bounding_box.x2,
                            'y2': result.detection.bounding_box.y2
                        },
                        'area_deteccao': result.detection.confidence
                    }
                    placas.append(placa_info)
            
            return placas
            
        except Exception as e:
            logger.error(f"Erro ao reconhecer múltiplas placas: {e}")
            return []

    def obter_estatisticas(self) -> dict:
        """
        Retorna estatísticas do sistema FastALPR.
        
        Returns:
            dict: Estatísticas do sistema
        """
        return {
            'sistema': 'FastALPR',
            'detector': 'YOLO v9 (384px)',
            'ocr': 'fast-plate-ocr (CCT-XS-v1)',
            'status': 'ativo' if self.alpr is not None else 'inativo',
            'dispositivo': 'auto'  # GPU se disponível, senão CPU
        }


# Instância global do serviço
anpr_service = ANPRService()