/**
 * Tipos TypeScript para o sistema de placas.
 */

export interface Placa {
  _id: string;
  placa: string;
  filename: string;
  image_base64: string;
  hora_entrada: string;
  hora_saida: string | null | undefined;
}

export interface PlacaUpdate {
  placa?: string;
  hora_entrada?: string;
  hora_saida?: string;
}

export interface PlacaSearchRequest {
  placa: string;
}

export interface ImageUploadResponse {
  placa: string;
  image_base64: string;
  success: boolean;
  message?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}
