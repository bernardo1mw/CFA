'use client';

import { ImageUploadResponse } from '@/types/placa';
import Image from 'next/image';

interface PlacaResultProps {
  result: ImageUploadResponse;
}

export default function PlacaResult({ result }: PlacaResultProps) {
  return (
    <div className="w-full max-w-md mx-auto space-y-4">
      <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
        <h2 className="text-xl font-bold text-green-400 mb-2">
          ✅ Placa Detectada: {result.placa}
        </h2>
        <p className="text-green-300 text-sm mb-4">
          {result.message || 'Placa reconhecida com sucesso!'}
        </p>
        
        <div className="space-y-2">
          <Image
            src={`data:image/png;base64,${result.image_base64}`}
            alt="Resultado do reconhecimento"
            width={400}
            height={300}
            className="w-full rounded-md border border-green-500/30"
          />
        </div>
      </div>
    </div>
  );
}
