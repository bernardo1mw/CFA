/**
 * Serviço de API para comunicação com o backend.
 */

import axios from 'axios';
import { Placa, PlacaUpdate, PlacaSearchRequest, ImageUploadResponse } from '@/types/placa';

// Configuração base da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos para processamento de imagens
});

/**
 * Serviço para operações com placas.
 */
export class PlacaService {
  /**
   * Upload de imagem para reconhecimento de placa.
   */
  static async uploadImage(file: File): Promise<ImageUploadResponse> {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await api.post('/api/placas/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  /**
   * Upload de imagem capturada da câmera (base64).
   */
  static async uploadCameraImage(imageBase64: string): Promise<ImageUploadResponse> {
    const formData = new FormData();
    formData.append('image_base64', imageBase64);
    
    const response = await api.post('/api/placas/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  /**
   * Lista todas as placas.
   */
  static async getAllPlacas(limit: number = 100): Promise<Placa[]> {
    const response = await api.get(`/api/placas/?limit=${limit}`);
    return response.data;
  }

  /**
   * Busca uma placa pelo ID.
   */
  static async getPlacaById(id: string): Promise<Placa> {
    const response = await api.get(`/api/placas/${id}`);
    return response.data;
  }

  /**
   * Busca uma placa pelo número.
   */
  static async searchPlaca(searchRequest: PlacaSearchRequest): Promise<Placa> {
    const response = await api.post('/api/placas/search', searchRequest);
    return response.data;
  }

  /**
   * Atualiza uma placa.
   */
  static async updatePlaca(id: string, updateData: PlacaUpdate): Promise<Placa> {
    const response = await api.put(`/api/placas/${id}`, updateData);
    return response.data;
  }

  /**
   * Deleta uma placa.
   */
  static async deletePlaca(id: string): Promise<{ message: string }> {
    const response = await api.delete(`/api/placas/${id}`);
    return response.data;
  }
}

export default api;
