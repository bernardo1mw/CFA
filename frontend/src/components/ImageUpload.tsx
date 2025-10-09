'use client';

import { useState, useRef } from 'react';
import { PlacaService } from '@/lib/api';
import { ImageUploadResponse } from '@/types/placa';
import Image from 'next/image';

interface ImageUploadProps {
  onUploadSuccess: (result: ImageUploadResponse) => void;
  onUploadError: (error: string) => void;
}

export default function ImageUpload({ onUploadSuccess, onUploadError }: ImageUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await PlacaService.uploadImage(file);
      onUploadSuccess(result);
    } catch (error: any) {
      onUploadError(error.response?.data?.detail || 'Erro ao processar imagem');
    } finally {
      setIsUploading(false);
    }
  };

  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setShowCamera(true);
      }
    } catch (error) {
      onUploadError('Erro ao acessar a câmera');
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        context.drawImage(videoRef.current, 0, 0);
        
        const dataURL = canvasRef.current.toDataURL('image/png');
        setCapturedImage(dataURL);
        
        // Para o vídeo
        const stream = videoRef.current.srcObject as MediaStream;
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        
        setShowCamera(false);
      }
    }
  };

  const uploadCapturedImage = async () => {
    if (!capturedImage) return;

    setIsUploading(true);
    try {
      const result = await PlacaService.uploadCameraImage(capturedImage);
      onUploadSuccess(result);
      setCapturedImage(null);
    } catch (error: any) {
      onUploadError(error.response?.data?.detail || 'Erro ao processar imagem capturada');
    } finally {
      setIsUploading(false);
    }
  };

  const resetUpload = () => {
    setCapturedImage(null);
    setShowCamera(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-md mx-auto space-y-4">
      {/* Upload de arquivo */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          Escolha uma imagem:
        </label>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          disabled={isUploading}
          className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-600 file:text-white hover:file:bg-blue-700 disabled:opacity-50"
        />
      </div>

      {/* Botão da câmera */}
      <div className="flex gap-2">
        <button
          onClick={openCamera}
          disabled={isUploading}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
        >
          📷 Tirar Foto
        </button>
        
        {capturedImage && (
          <button
            onClick={uploadCapturedImage}
            disabled={isUploading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            {isUploading ? 'Processando...' : 'Enviar Foto'}
          </button>
        )}
      </div>

      {/* Câmera */}
      {showCamera && (
        <div className="space-y-2">
          <video
            ref={videoRef}
            autoPlay
            className="w-full rounded-md"
          />
          <button
            onClick={capturePhoto}
            className="w-full bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            📸 Capturar
          </button>
        </div>
      )}

      {/* Imagem capturada */}
      {capturedImage && (
        <div className="space-y-2">
          <Image
            src={capturedImage}
            alt="Imagem capturada"
            width={400}
            height={300}
            className="w-full rounded-md"
          />
          <button
            onClick={resetUpload}
            className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Capturar Nova Foto
          </button>
        </div>
      )}

      {/* Canvas oculto para captura */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Loading */}
      {isUploading && (
        <div className="text-center text-blue-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p className="mt-2">Processando imagem...</p>
        </div>
      )}
    </div>
  );
}
