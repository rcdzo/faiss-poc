"""
IndexBuilder: Construção de índices FAISS por campo de endereço
"""
import os
from pathlib import Path
import pandas as pd
import numpy as np
import faiss
import pickle
from .embedding_service import EmbeddingService


class IndexBuilder:
    """Construtor de índices FAISS para busca vetorial de endereços"""
    
    def __init__(self, embedding_service: EmbeddingService):
        """
        Inicializa o construtor de índices
        
        Args:
            embedding_service: Serviço de embeddings
        """
        self.embedding_service = embedding_service
        self.indices = {}
        self.dataframe = None
    
    def build_indices(self, df: pd.DataFrame, fields: list = None) -> dict:
        """
        Constrói índices FAISS para cada campo
        
        Args:
            df: DataFrame com colunas [logradouro, bairro, cidade, uf, cep]
            fields: Lista de campos para indexar (default: ['logradouro', 'bairro', 'cidade'])
            
        Returns:
            Dicionário com índices FAISS por campo
        """
        if fields is None:
            fields = ['logradouro', 'bairro', 'cidade']
        
        self.dataframe = df.copy()
        n_records = len(df)
        
        print(f"Construindo índices FAISS para {n_records} endereços")
        
        for field in fields:
            # Preenche valores vazios
            texts = df[field].fillna('').astype(str).tolist()
            
            # Gera embeddings em batch
            embeddings = self.embedding_service.embed_batch(texts)
            
            # Cria índice FAISS (IndexFlatL2 para busca exata)
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            
            # Adiciona embeddings ao índice
            index.add(embeddings)
            
            self.indices[field] = index
        
        return self.indices
    
    def save_indices(self, output_dir: str):
        """
        Salva índices FAISS e dataframe em disco
        
        Args:
            output_dir: Diretório para salvar os arquivos
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Salva cada índice FAISS
        for field, index in self.indices.items():
            index_file = output_path / f"{field}_index.faiss"
            faiss.write_index(index, str(index_file))
        
        # Salva dataframe original
        df_file = output_path / "addresses.parquet"
        self.dataframe.to_parquet(df_file, index=False)
        
        # Salva metadados
        metadata = {
            'fields': list(self.indices.keys()),
            'n_records': len(self.dataframe),
            'embedding_dim': self.embedding_service.embedding_dim
        }
        metadata_file = output_path / "metadata.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump(metadata, f)
    
    def load_indices(self, input_dir: str):
        """
        Carrega índices FAISS e dataframe do disco
        
        Args:
            input_dir: Diretório com os arquivos salvos
        """
        input_path = Path(input_dir)
        
        # Carrega metadados
        metadata_file = input_path / "metadata.pkl"
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        
        # Carrega dataframe
        df_file = input_path / "addresses.parquet"
        self.dataframe = pd.read_parquet(df_file)
        
        # Carrega índices FAISS
        for field in metadata['fields']:
            index_file = input_path / f"{field}_index.faiss"
            self.indices[field] = faiss.read_index(str(index_file))
        
        return self.indices, self.dataframe
