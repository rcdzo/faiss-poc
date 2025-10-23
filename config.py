"""
Configurações da POC de Busca Vetorial DNE
"""

# Modelo de embeddings
EMBEDDING_MODEL = "neuralmind/bert-base-portuguese-cased"

# Campos para indexação
INDEXED_FIELDS = ['logradouro', 'bairro', 'cidade']

# Pesos de scoring
WEIGHTS_WITH_CEP = {
    'cep': 0.30,
    'logradouro': 0.40,
    'bairro': 0.20,
    'cidade': 0.10
}

WEIGHTS_WITHOUT_CEP = {
    'logradouro': 0.55,
    'bairro': 0.25,
    'cidade': 0.20
}

# UF usado como filtro bloqueante (não como peso no scoring)
# Quando UF está presente na query, filtra resultados apenas daquele estado
USE_UF_AS_FILTER = True

# Threshold de confiança
CONFIDENCE_THRESHOLD = 0.8

# Parâmetros de busca
DEFAULT_TOP_K = 5
DEFAULT_SEARCH_K = 100  # Candidatos intermediários por campo

# Paths
DATA_DIR = 'data'
INDICES_DIR = 'data/indices'
NOTEBOOKS_DIR = 'notebooks'

# Dataset sintético
SYNTHETIC_DATASET_SIZE = 10000
CLEAN_RATIO = 0.85  # 85% registros limpos
EMPTY_BAIRRO_RATIO = 0.05
ABBREVIATION_RATIO = 0.05
TYPO_RATIO = 0.05

# Queries de teste
TEST_QUERIES_SIZE = 150
CEP_WRONG_RATIO = 0.30
QUERY_ABBREVIATION_RATIO = 0.40
QUERY_TYPO_RATIO = 0.20
EMPTY_FIELDS_RATIO = 0.10

# Configurações FAISS
FAISS_INDEX_TYPE = 'IndexFlatL2'  # Busca exata com distância L2
BATCH_SIZE = 32  # Batch size para geração de embeddings

# Normalização de texto
NORMALIZE_ABBREVIATIONS = True
APPLY_UNIDECODE = True
APPLY_LOWERCASE = True
REMOVE_PUNCTUATION = True
