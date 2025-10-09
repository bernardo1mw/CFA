'use client';

import { useState } from 'react';
import Link from 'next/link';
import { PlacaService } from '@/lib/api';
import { Placa } from '@/types/placa';
import Image from 'next/image';

export default function BuscarPage() {
  const [placa, setPlaca] = useState('');
  const [resultado, setResultado] = useState<Placa | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!placa.trim()) return;

    setLoading(true);
    setError(null);
    setResultado(null);

    try {
      const data = await PlacaService.searchPlaca({ placa: placa.trim() });
      setResultado(data);
    } catch (error: any) {
      if (error.response?.status === 404) {
        setError(`A placa ${placa.toUpperCase()} não foi encontrada no sistema.`);
      } else {
        setError('Erro ao buscar placa');
      }
      console.error('Erro ao buscar placa:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-green-400">
            🔍 Buscar Placa
          </h1>
          <Link
            href="/"
            className="inline-block text-blue-400 hover:text-blue-300 transition-colors"
          >
            ⬅ Voltar
          </Link>
        </div>

        {/* Formulário de busca */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Número da Placa:
              </label>
              <input
                type="text"
                value={placa}
                onChange={(e) => setPlaca(e.target.value.toUpperCase())}
                placeholder="Digite a placa (ex: ABC-1234)"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading || !placa.trim()}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </form>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400 mx-auto"></div>
            <p className="mt-2 text-gray-300">Buscando placa...</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
            <p className="text-red-400 font-medium">❌ {error}</p>
          </div>
        )}

        {/* Resultado */}
        {resultado && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-green-400 mb-4">Resultado:</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Informações da placa */}
              <div className="space-y-3">
                <div>
                  <span className="text-gray-400 text-sm">Placa:</span>
                  <p className="text-xl font-bold text-white">{resultado.placa}</p>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Entrada:</span>
                  <p className="text-white">{resultado.hora_entrada}</p>
                </div>
                <div>
                  <span className="text-gray-400 text-sm">Saída:</span>
                  <p className="text-white">
                    {resultado.hora_saida || 'Ainda no estacionamento'}
                  </p>
                </div>
              </div>

              {/* Imagem */}
              <div>
                <Image
                  src={`data:image/png;base64,${resultado.image_base64}`}
                  alt="Imagem da placa"
                  width={400}
                  height={300}
                  className="w-full rounded-lg border border-gray-600"
                />
              </div>
            </div>

            {/* Botão de editar */}
            <div className="mt-6">
              <Link
                href={`/editar/${resultado._id}`}
                className="inline-block bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                ✏️ Editar Registro
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
