'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { PlacaService } from '@/lib/api';
import { Placa } from '@/types/placa';
import Image from 'next/image';

export default function RegistrosPage() {
  const [placas, setPlacas] = useState<Placa[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadPlacas();
  }, []);

  const loadPlacas = async () => {
    try {
      setLoading(true);
      const data = await PlacaService.getAllPlacas();
      setPlacas(data);
      setError(null);
    } catch (error: any) {
      setError('Erro ao carregar registros');
      console.error('Erro ao carregar placas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este registro?')) {
      return;
    }

    try {
      setDeletingId(id);
      await PlacaService.deletePlaca(id);
      setPlacas(placas.filter(placa => placa._id !== id));
    } catch (error: any) {
      setError('Erro ao excluir registro');
      console.error('Erro ao excluir placa:', error);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
          <p className="mt-4 text-gray-300">Carregando registros...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-blue-400">
              📋 Registros Salvos no MongoDB
            </h1>
            <p className="text-gray-300 mt-2">
              {placas.length} registro(s) encontrado(s)
            </p>
          </div>
          <Link
            href="/"
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            ⬅ Voltar para Upload
          </Link>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
            <p className="text-red-400 font-medium">❌ {error}</p>
          </div>
        )}

        {/* Registros */}
        {placas.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            <p className="text-gray-300 text-lg">Nenhum registro encontrado.</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {placas.map((placa) => (
              <div
                key={placa._id}
                className="bg-gray-800 rounded-lg p-6 border border-gray-700"
              >
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Informações da placa */}
                  <div className="space-y-3">
                    <div>
                      <span className="text-gray-400 text-sm">Placa:</span>
                      <p className="text-xl font-bold text-white">{placa.placa}</p>
                    </div>
                    <div>
                      <span className="text-gray-400 text-sm">Entrada:</span>
                      <p className="text-white">{placa.hora_entrada}</p>
                    </div>
                    <div>
                      <span className="text-gray-400 text-sm">Saída:</span>
                      <p className="text-white">
                        {placa.hora_saida || 'Ainda no estacionamento'}
                      </p>
                    </div>
                  </div>

                  {/* Imagem */}
                  <div className="space-y-3">
                    <Image
                      src={`data:image/png;base64,${placa.image_base64}`}
                      alt="Imagem da placa"
                      width={400}
                      height={300}
                      className="w-full rounded-lg border border-gray-600"
                    />
                  </div>
                </div>

                {/* Botões de ação */}
                <div className="flex flex-col sm:flex-row gap-3 mt-6">
                  <Link
                    href={`/editar/${placa._id}`}
                    className="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-center"
                  >
                    ✏️ Editar
                  </Link>
                  <button
                    onClick={() => handleDelete(placa._id)}
                    disabled={deletingId === placa._id}
                    className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                  >
                    {deletingId === placa._id ? 'Excluindo...' : '🗑 Excluir'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
