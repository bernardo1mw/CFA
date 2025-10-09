'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { PlacaService } from '@/lib/api';
import { Placa, PlacaUpdate } from '@/types/placa';
import Image from 'next/image';

export default function EditarPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [placa, setPlaca] = useState<Placa | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form data
  const [formData, setFormData] = useState({
    placa: '',
    hora_entrada: '',
    hora_saida: ''
  });

  useEffect(() => {
    if (id) {
      loadPlaca();
    }
  }, [id]);

  const loadPlaca = async () => {
    try {
      setLoading(true);
      const data = await PlacaService.getPlacaById(id);
      setPlaca(data);
      setFormData({
        placa: data.placa,
        hora_entrada: data.hora_entrada,
        hora_saida: data.hora_saida || ''
      });
      setError(null);
    } catch (error: any) {
      setError('Erro ao carregar registro');
      console.error('Erro ao carregar placa:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!placa) return;

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const updateData: PlacaUpdate = {
        placa: formData.placa,
        hora_entrada: formData.hora_entrada,
        hora_saida: formData.hora_saida || undefined
      };

      await PlacaService.updatePlaca(id, updateData);
      setSuccess('Dados atualizados com sucesso!');
      
      // Redireciona após 2 segundos
      setTimeout(() => {
        router.push('/registros');
      }, 2000);
    } catch (error: any) {
      setError('Erro ao atualizar registro');
      console.error('Erro ao atualizar placa:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto"></div>
          <p className="mt-4 text-gray-300">Carregando registro...</p>
        </div>
      </div>
    );
  }

  if (!placa) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-lg">Registro não encontrado.</p>
          <Link
            href="/registros"
            className="inline-block mt-4 text-blue-400 hover:text-blue-300 transition-colors"
          >
            ⬅ Voltar para registros
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-yellow-400">
            ✏️ Editar Registro
          </h1>
          <Link
            href="/buscar"
            className="inline-block text-blue-400 hover:text-blue-300 transition-colors"
          >
            ⬅ Voltar para busca
          </Link>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
            <p className="text-green-400 font-medium">✅ {success}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
            <p className="text-red-400 font-medium">❌ {error}</p>
          </div>
        )}

        {/* Formulário */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Placa:
              </label>
              <input
                type="text"
                name="placa"
                value={formData.placa}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Hora de Entrada:
              </label>
              <input
                type="text"
                name="hora_entrada"
                value={formData.hora_entrada}
                onChange={handleInputChange}
                placeholder="YYYY-MM-DD HH:MM:SS"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Hora de Saída:
              </label>
              <input
                type="text"
                name="hora_saida"
                value={formData.hora_saida}
                onChange={handleInputChange}
                placeholder="YYYY-MM-DD HH:MM:SS (opcional)"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              {saving ? 'Salvando...' : 'Salvar Alterações'}
            </button>
          </form>
        </div>

        {/* Imagem atual */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-medium text-gray-300 mb-4">Imagem Atual:</h3>
          <Image
            src={`data:image/png;base64,${placa.image_base64}`}
            alt="Imagem da placa"
            width={400}
            height={300}
            className="w-full rounded-lg border border-gray-600"
          />
        </div>
      </div>
    </div>
  );
}
