# Guia de Início Rápido - POC Busca Vetorial DNE

## Instalação

### 1. Ativar ambiente virtual (se ainda não estiver ativo)

```powershell
`C:\Users\rik_d\OneDrive\Documentos\Projetos\Backend\IA\genia\venv\Scripts\Activate.ps1`
```

### 2. Verificar instalação

```powershell
cd dne_poc
python validate.py
```

Se tudo estiver ✓, prossiga!

## Execução

### Opção 1: Usando Jupyter Notebook (Recomendado)

#### Passo 1: Gerar dataset sintético

```powershell
jupyter notebook
```

No navegador:

1. Abra `notebooks/generate_synthetic_dne.ipynb`
2. Execute todas as células (Cell > Run All)
3. Aguarde a geração de ~10k endereços

Arquivos gerados:

- `data/dne_sample.parquet` - Dataset com 10k endereços
- `data/test_queries.parquet` - 150 queries categorizadas
- `data/dne_sample_preview.csv` - Preview para inspeção
- `data/test_queries_preview.csv` - Preview das queries

#### Passo 2: Executar POC e validar resultados

No navegador:

1. Abra `notebooks/busca_vetorial_poc.ipynb`
2. Execute todas as células (Cell > Run All)
3. Observe os resultados:
   - Carregamento do modelo
   - Construção dos índices FAISS
   - Testes exploratórios
   - Validação sistemática por categoria
   - Métricas de precisão

### Opção 2: Usando script Python

Após gerar o dataset e construir os índices (via notebooks), você pode usar:

```powershell
python search.py
```

Para personalizar a busca, edite o arquivo `search.py` e modifique a chamada da função `search_address()`.

## Estrutura dos Resultados

A busca retorna JSON estruturado:

```json
{
  "results": [
    {
      "address": {
        "logradouro": "Rua das Flores",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "uf": "SP",
        "cep": "01310-100"
      },
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

## Interpretação dos Resultados

### Níveis de Confiança

- **high** (score ≥ 0.8): Alta confiança - pode sugerir correção de CEP
- **medium** (0.6 ≤ score < 0.8): Média confiança
- **low** (score < 0.6): Baixa confiança

### Scores por Campo

- Mostra similaridade individual de cada campo (0 a 1)
- Útil para entender qual campo contribuiu mais/menos para o score final
- Ajuda a diagnosticar problemas de precisão

## Casos de Uso

### 1. CEP Errado, mas Rua/Bairro Corretos

**Objetivo:** Sistema deve sugerir o CEP correto

Query:

```python
{
  "logradouro": "Rua das Flores",
  "bairro": "Centro",
  "cidade": "São Paulo",
  "uf": "SP",
  "cep": "20000-000"  # CEP do RJ, mas endereço é de SP
}
```

**Esperado:** Resultado com score alto (≥0.8) mesmo com CEP divergente

### 2. Campos Vazios

**Objetivo:** Busca deve funcionar com campos parciais

Query:

```python
{
  "logradouro": "",
  "bairro": "Centro",
  "cidade": "São Paulo",
  "uf": "SP",
  "cep": ""
}
```

**Esperado:** Pesos ajustados dinamicamente, resultado baseado em bairro+cidade

### 3. Abreviações

**Objetivo:** Normalização deve lidar com R., Av., etc.

Query:

```python
{
  "logradouro": "R. das Flores",  # ou "Rua das Flores"
  "bairro": "Jd. Europa",         # ou "Jardim Europa"
  "cidade": "São Paulo",
  "uf": "SP",
  "cep": "01310-100"
}
```

**Esperado:** Mesmo resultado independente da abreviação

### 4. Typos Leves

**Objetivo:** Embeddings devem capturar similaridade semântica

Query:

```python
{
  "logradouro": "Rua das Floers",  # Typo: Floers → Flores
  "bairro": "Centro",
  "cidade": "São Paulo",
  "uf": "SP",
  "cep": "01310-100"
}
```

**Esperado:** Score ainda alto devido à similaridade vetorial

## Ajuste de Parâmetros

Edite `config.py` para ajustar:

```python
# Pesos com CEP
WEIGHTS_WITH_CEP = {
    'cep': 0.30,        # Ajuste conforme necessário
    'logradouro': 0.40,
    'bairro': 0.20,
    'cidade': 0.10
}

# Threshold de confiança
CONFIDENCE_THRESHOLD = 0.8  # Aumente para ser mais rigoroso
```

## Troubleshooting

### Erro: "Índices não encontrados"

**Solução:** Execute primeiro `notebooks/generate_synthetic_dne.ipynb` e depois `notebooks/busca_vetorial_poc.ipynb`

### Erro: ModuleNotFoundError

**Solução:** `pip install -r requirements.txt`

### Modelo demorando para carregar

**Normal:** Na primeira execução, o modelo (~400MB) é baixado. Execuções subsequentes usam cache.

### Baixa precisão

**Possíveis causas:**

1. Pesos inadequados para o caso de uso → Ajuste em `config.py`
2. Dataset sintético não representa dados reais → Use dados reais do DNE
3. Threshold muito alto → Reduza para 0.7 ou 0.75

## Próximos Passos

1. **Teste com dados reais:** Substitua `dne_sample.parquet` por dados reais do DNE
2. **Fine-tuning:** Se precisão for insuficiente, considere fine-tuning do modelo
3. **Otimização:** Para produção, use FAISS com GPU ou índices aproximados (IVF)
4. **API:** Crie API REST com FastAPI para integração
5. **Cache:** Implemente cache de embeddings para queries frequentes

## Referências

- **Modelo:** [rufimelo/bert-base-portuguese-cased-nli-assin-2](https://huggingface.co/rufimelo/bert-base-portuguese-cased-nli-assin-2)
- **FAISS:** [Facebook AI Similarity Search](https://github.com/facebookresearch/faiss)
- **Sentence Transformers:** [Documentation](https://www.sbert.net/)
