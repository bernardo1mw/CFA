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
            # Threshold reduzido de 0.4 para 0.25 para detectar mais placas
            self.alpr = ALPR(
                detector_model="yolo-v9-t-384-license-plate-end2end",
                detector_conf_thresh=0.25,  # Reduzido para detectar mais placas
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

    def preprocessar_imagem(self, imagem: np.ndarray) -> list[np.ndarray]:
        """
        Pré-processa a imagem com diferentes técnicas para melhorar a detecção.
        
        Args:
            imagem: Imagem original
            
        Returns:
            Lista de imagens pré-processadas
        """
        imagens_processadas = [imagem]  # Sempre inclui a original
        
        # 1. Ajuste de brilho e contraste (CLAHE)
        lab = cv2.cvtColor(imagem, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        imagem_clahe = cv2.merge([l, a, b])
        imagem_clahe = cv2.cvtColor(imagem_clahe, cv2.COLOR_LAB2BGR)
        imagens_processadas.append(imagem_clahe)
        
        # 2. Sharpening (nitidez)
        kernel_sharpen = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
        imagem_sharp = cv2.filter2D(imagem, -1, kernel_sharpen)
        imagens_processadas.append(imagem_sharp)
        
        # 3. Aumento de contraste
        alpha = 1.5  # Contraste
        beta = 10    # Brilho
        imagem_contraste = cv2.convertScaleAbs(imagem, alpha=alpha, beta=beta)
        imagens_processadas.append(imagem_contraste)
        
        # 4. Combinação CLAHE + Sharpening
        lab_sharp = cv2.cvtColor(imagem_sharp, cv2.COLOR_BGR2LAB)
        l_sharp, a_sharp, b_sharp = cv2.split(lab_sharp)
        l_sharp = clahe.apply(l_sharp)
        imagem_combinada = cv2.merge([l_sharp, a_sharp, b_sharp])
        imagem_combinada = cv2.cvtColor(imagem_combinada, cv2.COLOR_LAB2BGR)
        imagens_processadas.append(imagem_combinada)
        
        return imagens_processadas
    
    def validar_tamanho_placa(self, bbox, imagem_shape: tuple) -> bool:
        """
        Valida se a placa detectada tem tamanho mínimo razoável.
        
        Args:
            bbox: Bounding box da placa
            imagem_shape: Dimensões da imagem (altura, largura)
            
        Returns:
            bool: True se o tamanho é válido
        """
        altura_img, largura_img = imagem_shape[:2]
        largura_placa = bbox.x2 - bbox.x1
        altura_placa = bbox.y2 - bbox.y1
        
        # Placa deve ter pelo menos 2% da largura e 1% da altura da imagem
        largura_min = largura_img * 0.02
        altura_min = altura_img * 0.01
        
        # Placa não deve ser muito pequena (menos de 30x10 pixels)
        if largura_placa < max(30, largura_min) or altura_placa < max(10, altura_min):
            return False
        
        # Placa não deve ser muito grande (mais de 80% da imagem)
        if largura_placa > largura_img * 0.8 or altura_placa > altura_img * 0.8:
            return False
        
        # Razão aspecto deve ser razoável (placas são mais largas que altas)
        razao = largura_placa / altura_placa if altura_placa > 0 else 0
        if razao < 1.5 or razao > 8.0:  # Placas geralmente têm razão entre 2:1 e 5:1
            return False
        
        return True

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
        Tenta múltiplas estratégias de pré-processamento para maximizar detecção.
        
        Args:
            imagem: Imagem de entrada (numpy array)
            
        Returns:
            tuple: (texto_placa, imagem_resultado)
        """
        if self.alpr is None:
            logger.error("FastALPR não inicializado.")
            return None, None
        
        try:
            logger.info("Processando imagem com FastALPR (múltiplas estratégias)...")
            
            # Gera diferentes versões pré-processadas da imagem
            imagens_processadas = self.preprocessar_imagem(imagem)
            
            melhor_resultado_global = None
            melhor_confianca = 0.0
            melhor_imagem = imagem
            
            # Tenta detectar em cada versão pré-processada
            for idx, img_processada in enumerate(imagens_processadas):
                try:
                    logger.debug(f"Tentativa {idx + 1}/{len(imagens_processadas)}: processando imagem...")
                    
                    # Usa FastALPR para detectar e reconhecer placas
                    alpr_results = self.alpr.predict(img_processada)
                    
                    if not alpr_results:
                        continue
                    
                    # Filtra resultados válidos
                    resultados_validos = []
                    for result in alpr_results:
                        # Valida tamanho da placa
                        if not self.validar_tamanho_placa(result.detection.bounding_box, img_processada.shape):
                            logger.debug(f"Placa descartada: tamanho inválido")
                            continue
                        
                        # Valida confiança do OCR (mínimo 0.3)
                        if result.ocr and result.ocr.confidence and result.ocr.confidence >= 0.3:
                            resultados_validos.append(result)
                    
                    if not resultados_validos:
                        continue
                    
                    # Pega o resultado com maior confiança
                    melhor_resultado = max(resultados_validos, 
                                          key=lambda x: x.ocr.confidence if x.ocr else 0)
                    
                    if melhor_resultado.ocr is None or not melhor_resultado.ocr.text:
                        continue
                    
                    # Atualiza melhor resultado global
                    confianca_atual = melhor_resultado.ocr.confidence
                    if confianca_atual > melhor_confianca:
                        melhor_confianca = confianca_atual
                        melhor_resultado_global = melhor_resultado
                        melhor_imagem = img_processada
                        logger.debug(f"Nova melhor detecção encontrada (confiança: {confianca_atual:.2f})")
                
                except Exception as e:
                    logger.warning(f"Erro ao processar imagem {idx + 1}: {e}")
                    continue
            
            # Se não encontrou nenhuma placa válida
            if melhor_resultado_global is None:
                logger.info("Nenhuma placa válida detectada após todas as tentativas.")
                return None, imagem
            
            # Extrai o texto da placa
            texto_placa = melhor_resultado_global.ocr.text.strip()
            
            # Aplica filtros e correções se necessário
            texto_filtrado = self.filtrar_texto_placa(texto_placa)
            if texto_filtrado:
                texto_placa = texto_filtrado
            
            # Formata a placa
            texto_placa_formatado = self.formatar_placa(texto_placa)
            
            # Valida se o texto formatado é válido (deve ter 7 caracteres)
            if len(texto_placa_formatado.replace('-', '')) < 6:
                logger.warning(f"Texto da placa muito curto: {texto_placa_formatado}")
                return None, imagem
            
            logger.info(f"Placa reconhecida: {texto_placa_formatado} (confiança: {melhor_confianca:.2f})")
            
            # Gera imagem com anotações usando a melhor imagem processada
            imagem_resultado = self.alpr.draw_predictions(melhor_imagem)
            
            return texto_placa_formatado, imagem_resultado
            
        except Exception as e:
            logger.error(f"Erro durante reconhecimento: {e}", exc_info=True)
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