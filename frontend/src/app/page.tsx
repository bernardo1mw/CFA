'use client';

import { useState } from 'react';
import Link from 'next/link';
import ImageUpload from '@/components/ImageUpload';
import PlacaResult from '@/components/PlacaResult';
import { ImageUploadResponse } from '@/types/placa';

export default function Home() {
  const [uploadResult, setUploadResult] = useState<ImageUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUploadSuccess = (result: ImageUploadResponse) => {
    setUploadResult(result);
    setError(null);
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setUploadResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-blue-400">
            📸 PlacaView
          </h1>
          <p className="text-gray-300 text-lg">
            Reconhecimento de placas com um clique
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <ImageUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
            <p className="text-red-400 font-medium">❌ {error}</p>
          </div>
        )}

        {/* Result */}
        {uploadResult && (
          <PlacaResult result={uploadResult} />
        )}

        {/* Navigation Links */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/registros"
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors text-center"
          >
            📋 Ver Registros Salvos
          </Link>
          <Link
            href="/buscar"
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-lg transition-colors text-center"
          >
            🔍 Consultar Placa
          </Link>
        </div>
      </div>
    </div>
  );
}
