"""
EmbeddingService: Normalização de texto e geração de embeddings para endereços brasileiros
"""
import re
from typing import Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from unidecode import unidecode


class EmbeddingService:
    """Serviço para normalização e geração de embeddings de endereços"""
    
    def __init__(self, model_name: str = "neuralmind/bert-base-portuguese-cased"):
        """
        Inicializa o serviço de embeddings
        
        Args:
            model_name: Nome do modelo sentence-transformers
        """
        print(f"Carregando modelo de embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normaliza texto de endereço brasileiro
        
        Args:
            text: Texto original
            
        Returns:
            Texto normalizado
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove acentos
        text = unidecode(text)
        
        # Lowercase
        text = text.lower()
        
        # Normaliza abreviações comuns
        replacements = {
            r'\br\.?\s': 'rua ',
            r'\bav\.?\s': 'avenida ',
            r'\btrav\.?\s': 'travessa ',
            r'\balam\.?\s': 'alameda ',
            r'\bpca\.?\s': 'praca ',
            r'\bjd\.?\s': 'jardim ',
            r'\bvl\.?\s': 'vila ',
            r'\bcj\.?\s': 'conjunto ',
            r'\bqd\.?\s': 'quadra ',
            r'\blt\.?\s': 'lote ',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        # Remove pontuação extra, mantendo apenas espaços
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Gera embedding para um texto
        
        Args:
            text: Texto a ser embedado
            
        Returns:
            Vetor de embedding
        """
        normalized = self.normalize_text(text)
        if not normalized:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        return self.model.encode(normalized, convert_to_numpy=True, show_progress_bar=False)
    
    def embed_address_fields(self, address: Dict[str, str]) -> Dict[str, np.ndarray]:
        """
        Gera embeddings para cada campo do endereço
        
        Args:
            address: Dicionário com campos do endereço (logradouro, bairro, cidade, uf, cep)
            
        Returns:
            Dicionário com embeddings por campo
        """
        embeddings = {}
        
        for field in ['logradouro', 'bairro', 'cidade']:
            text = address.get(field, '')
            embeddings[field] = self.embed_text(text)
        
        return embeddings
    
    def embed_batch(self, texts: list) -> np.ndarray:
        """
        Gera embeddings para um lote de textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Matriz de embeddings (N x dim)
        """
        normalized_texts = [self.normalize_text(t) for t in texts]
        
        # Substitui textos vazios por placeholder para evitar erros
        normalized_texts = [t if t else " " for t in normalized_texts]
        
        embeddings = self.model.encode(
            normalized_texts, 
            convert_to_numpy=True, 
            show_progress_bar=True,
            batch_size=32
        )
        
        return embeddings.astype(np.float32)
