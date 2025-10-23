# POC: Busca Vetorial para Enriquecimento de Endereços DNE

POC para validar se IA consegue substituir sistema ML de enriquecimento de endereços, usando busca vetorial multi-campo para resolver problemas de scores irreais quando campos estão vazios ou imprecisos.

## Problema

Sistema atual com FAISS IndexFlat32 + full-text indexing gera scores irreais quando:

- Campos estão vazios ou imprecisos
- CEP está errado mas rua/bairro corretos
- Query tem abreviações (R., Av.)
- Endereços válidos ficam de fora por validação monolítica

## Solução

**Busca vetorial multi-campo com pesos dinâmicos:**

- Embeddings separados por campo (logradouro, bairro, cidade)
- Índices FAISS independentes
- Scoring dinâmico ajustado por campos presentes na query
- Threshold 0.8 para sugestões de alta confiança
- Normalização de texto antes de embedar

## Estrutura

```
dne_poc/
├── src/
│   ├── embedding_service.py    # Normalização + embeddings
│   ├── index_builder.py         # Construção de índices FAISS
│   └── search_engine.py         # Busca com scoring dinâmico
├── notebooks/
│   ├── generate_synthetic_dne.ipynb   # Gera dataset sintético
│   └── busca_vetorial_poc.ipynb       # Validação completa
├── data/
│   ├── dne_sample.parquet       # 10k endereços sintéticos
│   ├── test_queries.parquet     # Queries categorizadas
│   └── indices/                 # Índices FAISS salvos
└── requirements.txt
```

## Uso

### 1. Gerar Dataset Sintético

Execute `notebooks/generate_synthetic_dne.ipynb`:

- Gera 10k endereços brasileiros com CEPs geográficos reais
- 85% registros limpos, 15% com variações
- 150 queries categorizadas (CEP errado, abreviações, typos, campos vazios)

### 2. Executar POC

Execute `notebooks/busca_vetorial_poc.ipynb`:

- Carrega modelo `rufimelo/bert-base-portuguese-cased-nli-assin-2`
- Constrói índices FAISS por campo
- Valida precisão em cenários problemáticos
- Gera métricas por categoria

## Configuração de Pesos

**Com CEP na query:**

- CEP: 30%
- Logradouro: 40%
- Bairro: 20%
- Cidade: 10%

**Sem CEP na query:**

- Logradouro: 55%
- Bairro: 25%
- Cidade: 20%

**UF:** Peso 0 (cidade já desambigua)

## Retorno da Busca

JSON estruturado:

```json
{
  "results": [
    {
      "address": {...},
      "score": 0.87,
      "confidence": "high",
      "field_scores": {
        "logradouro": 0.92,
        "bairro": 0.85,
        "cidade": 0.88
      }
    }
  ],
  "query": {...},
  "total_found": 5,
  "weights_used": {...}
}
```

## Threshold de Confiança

- **score ≥ 0.8:** Alta confiança (pode sugerir correção de CEP)
- **0.6 ≤ score < 0.8:** Média confiança
- **score < 0.6:** Baixa confiança

## Dependências Principais

- `sentence-transformers` (modelo de embeddings)
- `faiss-cpu` (busca vetorial)
- `pandas` + `pyarrow` (manipulação de dados)
- `unidecode` (normalização de texto)

## Características

✅ Código Python simples e preciso  
✅ Foco na precisão da busca  
✅ Prints apenas em etapas críticas  
✅ Retorna top-5 sempre  
✅ Campos vazios não penalizam score  
✅ Sugestão de CEP quando score ≥ 0.8
