"""
Script simples para testar a busca de endereços via linha de comando
"""
import sys
import json
from pathlib import Path
import pandas as pd

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.embedding_service import EmbeddingService
from src.index_builder import IndexBuilder
from src.search_engine import SearchEngine


def load_or_build_search_engine():
    """Carrega ou constrói motor de busca"""
    data_path = Path(__file__).parent / 'data'
    indices_path = data_path / 'indices'
    
    # Inicializa serviço de embeddings
    embedding_service = EmbeddingService()
    
    # Verifica se índices existem
    if (indices_path / 'metadata.pkl').exists():
        print("Carregando índices existentes...")
        index_builder = IndexBuilder(embedding_service)
        indices, dataframe = index_builder.load_indices(str(indices_path))
    else:
        print("Índices não encontrados. Execute primeiro o notebook generate_synthetic_dne.ipynb")
        print("e depois o notebook busca_vetorial_poc.ipynb para construir os índices.")
        sys.exit(1)
    
    # Inicializa motor de busca
    search_engine = SearchEngine(
        embedding_service=embedding_service,
        indices=indices,
        dataframe=dataframe
    )
    
    return search_engine


def search_address(logradouro='', bairro='', cidade='', uf='', cep='', top_k=5):
    """
    Busca endereços
    
    Args:
        logradouro: Nome da rua
        bairro: Nome do bairro
        cidade: Nome da cidade
        uf: Sigla do estado
        cep: CEP
        top_k: Número de resultados
    """
    search_engine = load_or_build_search_engine()
    
    query = {
        'logradouro': logradouro,
        'bairro': bairro,
        'cidade': cidade,
        'uf': uf,
        'cep': cep
    }
    
    print(f"\nBuscando por: {query}\n")
    result_json = search_engine.search(query, top_k=top_k)
    result = json.loads(result_json)
    
    print("="*70)
    print(f"RESULTADOS (Top-{top_k})")
    print("="*70)
    
    for i, res in enumerate(result['results'], 1):
        addr = res['address']
        print(f"\n#{i} - Score: {res['score']:.3f} | Confiança: {res['confidence'].upper()}")
        print(f"  Logradouro: {addr['logradouro']}")
        print(f"  Bairro: {addr['bairro']}")
        print(f"  Cidade: {addr['cidade']} - {addr['uf']}")
        print(f"  CEP: {addr['cep']}")
        
        if res.get('field_scores'):
            print(f"  Scores por campo: {json.dumps(res['field_scores'], indent=4)}")
    
    print("\n" + "="*70)
    print(f"Pesos utilizados: {result['weights_used']}")
    print("="*70)


if __name__ == '__main__':
    # Exemplo de uso
    if len(sys.argv) > 1:
        # Uso via argumentos de linha de comando (simplificado)
        print("Uso: python search.py")
        print("Para buscar, edite os parâmetros na função search_address() no código")
    else:
        # Exemplo de busca
        search_address(
            logradouro='Rua das Flores',
            bairro='Centro',
            cidade='São Paulo',
            uf='SP',
            cep='',
            top_k=5
        )
