"""
Serviço de conexão e operações com MongoDB.
"""

import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime


class DatabaseService:
    """Serviço para operações com o banco de dados MongoDB."""
    
    def __init__(self):
        """Inicializa a conexão com o MongoDB."""
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.database_name = os.getenv('DATABASE_NAME', 'ocr_db')
        self.collection_name = os.getenv('COLLECTION_NAME', 'placas')
        
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Testa a conexão
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print(f"✅ Conectado ao MongoDB: {self.mongodb_uri}")
        except Exception as e:
            print(f"❌ Erro ao conectar MongoDB: {e}")
            print("Tentando reconectar em 5 segundos...")
            import time
            time.sleep(5)
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]

    def create_placa(self, placa_data: Dict[str, Any]) -> str:
        """
        Cria um novo registro de placa.
        
        Args:
            placa_data: Dados da placa
            
        Returns:
            str: ID do registro criado
        """
        result = self.collection.insert_one(placa_data)
        return str(result.inserted_id)

    def get_placa_by_id(self, placa_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma placa pelo ID.
        
        Args:
            placa_id: ID da placa
            
        Returns:
            Dict com os dados da placa ou None se não encontrada
        """
        try:
            placa = self.collection.find_one({'_id': ObjectId(placa_id)})
            if placa:
                placa['_id'] = str(placa['_id'])
            return placa
        except Exception as e:
            print(f"Erro ao buscar placa por ID: {e}")
            return None

    def get_placa_by_number(self, placa_number: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma placa pelo número.
        
        Args:
            placa_number: Número da placa
            
        Returns:
            Dict com os dados da placa ou None se não encontrada
        """
        placa = self.collection.find_one({'placa': placa_number.upper()})
        if placa:
            placa['_id'] = str(placa['_id'])
        return placa

    def get_all_placas(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca todas as placas, ordenadas por data de criação (mais recentes primeiro).
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de placas
        """
        # Filtra apenas registros com placa válida (não nula)
        placas = list(self.collection.find({
            'placa': {'$ne': None, '$exists': True}
        }).sort('_id', -1).limit(limit))
        
        for placa in placas:
            placa['_id'] = str(placa['_id'])
        return placas

    def update_placa(self, placa_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Atualiza uma placa existente.
        
        Args:
            placa_id: ID da placa
            update_data: Dados para atualizar
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(placa_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Erro ao atualizar placa: {e}")
            return False

    def delete_placa(self, placa_id: str) -> bool:
        """
        Deleta uma placa.
        
        Args:
            placa_id: ID da placa
            
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            result = self.collection.delete_one({'_id': ObjectId(placa_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erro ao deletar placa: {e}")
            return False

    def clean_invalid_records(self) -> int:
        """
        Remove registros inválidos (com placa nula) do banco de dados.
        
        Returns:
            Número de registros removidos
        """
        result = self.collection.delete_many({
            'placa': {'$in': [None, '']}
        })
        return result.deleted_count

    def close_connection(self):
        """Fecha a conexão com o MongoDB."""
        if hasattr(self, 'client'):
            self.client.close()


# Instância global do serviço de banco
db_service = DatabaseService()
