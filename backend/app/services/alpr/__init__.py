"""
FastALPR package.
"""

from .alpr import ALPR, ALPRResult
from .base import BaseDetector, BaseOCR, DetectionResult, OcrResult

__all__ = ["ALPR", "ALPRResult", "BaseDetector", "BaseOCR", "DetectionResult", "OcrResult"]
