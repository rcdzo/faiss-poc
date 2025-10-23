"""
SearchEngine: Motor de busca com scoring dinâmico e multi-campo
"""
import json
from typing import Dict, List, Optional
import numpy as np
import faiss
import pandas as pd
from .embedding_service import EmbeddingService


class SearchEngine:
    """Motor de busca vetorial com pesos dinâmicos por campo"""
    
    def __init__(
        self, 
        embedding_service: EmbeddingService,
        indices: Dict[str, faiss.Index],
        dataframe: pd.DataFrame
    ):
        """
        Inicializa o motor de busca
        
        Args:
            embedding_service: Serviço de embeddings
            indices: Dicionário com índices FAISS por campo
            dataframe: DataFrame original com endereços
        """
        self.embedding_service = embedding_service
        self.indices = indices
        self.dataframe = dataframe
        
        # Pesos base por campo
        self.base_weights = {
            'with_cep': {
                'cep': 0.30,
                'logradouro': 0.40,
                'bairro': 0.20,
                'cidade': 0.10
            },
            'without_cep': {
                'logradouro': 0.55,
                'bairro': 0.25,
                'cidade': 0.20
            }
        }
        
        self.confidence_threshold = 0.8
        self.use_uf_filter = True
    
    def _get_dynamic_weights(self, query: Dict[str, str]) -> Dict[str, float]:
        """
        Calcula pesos dinâmicos baseado nos campos presentes na query
        
        Args:
            query: Dicionário com campos da query
            
        Returns:
            Dicionário com pesos normalizados
        """
        has_cep = bool(query.get('cep'))
        
        # Seleciona conjunto de pesos base
        if has_cep:
            weights = self.base_weights['with_cep'].copy()
        else:
            weights = self.base_weights['without_cep'].copy()
        
        # Remove pesos de campos ausentes e renormaliza
        available_fields = [f for f in ['logradouro', 'bairro', 'cidade'] if query.get(f)]
        
        # Filtra apenas campos disponíveis (exceto CEP que é tratado separadamente)
        filtered_weights = {k: v for k, v in weights.items() if k in available_fields or k == 'cep'}
        
        # Renormaliza pesos
        total_weight = sum(filtered_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v / total_weight for k, v in filtered_weights.items()}
        else:
            normalized_weights = filtered_weights
        
        return normalized_weights
    
    def _calculate_field_similarity(
        self, 
        field: str, 
        query_embedding: np.ndarray, 
        top_k: int = 100
    ) -> tuple:
        """
        Calcula similaridade para um campo específico
        
        Args:
            field: Nome do campo
            query_embedding: Embedding da query
            top_k: Número de resultados para buscar
            
        Returns:
            Tupla (distâncias, índices)
        """
        index = self.indices[field]
        
        # Busca os top_k mais próximos (menor distância L2)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        distances, indices = index.search(query_embedding, top_k)
        
        # Converte distância L2 para similaridade (0 a 1, onde 1 é mais similar)
        # Normalização: sim = 1 / (1 + distance)
        similarities = 1.0 / (1.0 + distances[0])
        
        return similarities, indices[0]
    
    def _calculate_cep_match(self, query_cep: str, db_cep: str) -> float:
        """
        Calcula match exato ou parcial de CEP
        
        Args:
            query_cep: CEP da query
            db_cep: CEP do banco
            
        Returns:
            Score de 0 a 1
        """
        if not query_cep or not db_cep:
            return 0.0
        
        # Remove formatação
        query_clean = query_cep.replace('-', '').replace('.', '')
        db_clean = db_cep.replace('-', '').replace('.', '')
        
        # Match exato
        if query_clean == db_clean:
            return 1.0
        
        # Match parcial (primeiros 5 dígitos - região)
        if len(query_clean) >= 5 and len(db_clean) >= 5:
            if query_clean[:5] == db_clean[:5]:
                return 0.5
        
        return 0.0
    
    def search(
        self, 
        query: Dict[str, str], 
        top_k: int = 5,
        search_k: int = 100
    ) -> str:
        """
        Realiza busca vetorial com scoring dinâmico
        
        Args:
            query: Dicionário com campos {logradouro, bairro, cidade, uf, cep}
            top_k: Número de resultados a retornar
            search_k: Número de candidatos intermediários por campo
            
        Returns:
            JSON string com resultados estruturados
        """
        # Calcula pesos dinâmicos
        weights = self._get_dynamic_weights(query)
        
        # Gera embeddings para campos da query
        query_embeddings = self.embedding_service.embed_address_fields(query)
        
        # Busca por campo e agrega scores
        candidate_scores = {}
        field_scores_map = {}
        
        for field in ['logradouro', 'bairro', 'cidade']:
            if not query.get(field):
                continue
            
            query_emb = query_embeddings[field]
            similarities, indices = self._calculate_field_similarity(field, query_emb, search_k)
            
            weight = weights.get(field, 0.0)
            
            for idx, sim in zip(indices, similarities):
                # Filtro por UF se fornecido (aumenta determinismo)
                if self.use_uf_filter and query.get('uf'):
                    db_uf = self.dataframe.iloc[idx]['uf']
                    if db_uf != query['uf']:
                        continue  # Bloqueia resultados de outros estados
                
                if idx not in candidate_scores:
                    candidate_scores[idx] = 0.0
                    field_scores_map[idx] = {}
                
                candidate_scores[idx] += weight * sim
                field_scores_map[idx][field] = float(sim)
        
        # Adiciona score de CEP se disponível
        if query.get('cep'):
            cep_weight = weights.get('cep', 0.0)
            for idx in candidate_scores.keys():
                db_cep = self.dataframe.iloc[idx]['cep']
                cep_score = self._calculate_cep_match(query.get('cep'), db_cep)
                candidate_scores[idx] += cep_weight * cep_score
                field_scores_map[idx]['cep'] = cep_score
        
        # Ordena por score e pega top_k
        sorted_candidates = sorted(
            candidate_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # Monta resultados
        results = []
        for idx, score in sorted_candidates:
            row = self.dataframe.iloc[idx]
            
            # Determina nível de confiança
            if score >= self.confidence_threshold:
                confidence = "high"
            elif score >= 0.6:
                confidence = "medium"
            else:
                confidence = "low"
            
            result = {
                "address": {
                    "logradouro": row['logradouro'],
                    "bairro": row['bairro'],
                    "cidade": row['cidade'],
                    "uf": row['uf'],
                    "cep": row['cep']
                },
                "score": float(score),
                "confidence": confidence,
                "field_scores": field_scores_map.get(idx, {})
            }
            results.append(result)
        
        # Monta resposta JSON
        response = {
            "results": results,
            "query": query,
            "total_found": len(results),
            "weights_used": weights
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
