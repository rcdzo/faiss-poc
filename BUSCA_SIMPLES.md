# 🎯 Guia de Uso: Busca Simples com Reranking

## 🚀 Como Usar

### 1. Abra o Notebook
```bash
jupyter notebook notebooks/poc_dne_gpu_t4_clean.ipynb
```

### 2. Execute as Células de Setup
Execute as células até aparecer:
```
✅ Função buscar_com_reranking() pronta!
```

### 3. Use a Função para Buscar

#### Forma Mais Simples
```python
buscar_com_reranking(
    logradouro="Avenida Paulista",
    bairro="Bela Vista",
    cidade="São Paulo",
    uf="SP"
)
```

#### Com CEP (Recomendado)
```python
buscar_com_reranking(
    logradouro="Avenida Paulista",
    bairro="Bela Vista",
    cidade="São Paulo",
    uf="SP",
    cep="01310-100"
)
```

#### Controlar Número de Resultados
```python
buscar_com_reranking(
    logradouro="Rua das Flores",
    bairro="Centro",
    cidade="Curitiba",
    uf="PR",
    top_k=10  # Mostra top 10 resultados
)
```

---

## 📋 Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `logradouro` | string | ✅ Sim | Nome da rua/avenida/travessa/etc |
| `bairro` | string | ✅ Sim | Nome do bairro |
| `cidade` | string | ✅ Sim | Nome da cidade |
| `uf` | string | ✅ Sim | Sigla do estado (SP, RJ, MG, etc) |
| `cep` | string | ❌ Não | CEP (formato: "12345-678" ou "12345678") |
| `top_k` | int | ❌ Não | Quantos resultados retornar (padrão: 5) |
| `verbose` | bool | ❌ Não | Mostrar detalhes (padrão: True) |

---

## 📊 Entendendo o Output

### Exemplo de Saída:
```
🔍 BUSCA COM RERANKING
================================================================================

📌 Query:
   Avenida Paulista
   Bela Vista - São Paulo/SP
   CEP: 01310-100

🎯 Resultados (Top 3):
================================================================================

1. 🟢 Score: 98.50% | Confiança: HIGH
   📍 Avenida Paulista
   📍 Bela Vista - São Paulo/SP
   📍 CEP: 01310-100
   📊 Scores:
      logradouro  : ██████████ 0.987
      bairro      : █████████░ 0.901
      cidade      : ██████████ 0.995
      cep         : ██████████ 1.000
   ✅ Aparece em TODOS os 4 campos!
```

### Símbolos de Confiança:
- 🟢 **Alta** (≥ 80%) - Resultado muito provável
- 🟡 **Média** (60-80%) - Resultado possível
- 🔴 **Baixa** (< 60%) - Resultado improvável

### Barra de Score:
```
██████████ 1.000  ← Perfeito (100%)
█████████░ 0.901  ← Muito bom (90%)
████████░░ 0.823  ← Bom (82%)
███░░░░░░░ 0.301  ← Fraco (30%)
```

### Interseção de Campos:
- **✅ Aparece em TODOS os N campos** → Altíssima confiabilidade
- **⚠️ Aparece em X/N campos** → Match parcial, menor confiança

---

## 💡 Exemplos Práticos

### Exemplo 1: Busca Completa (Dados Perfeitos)
```python
buscar_com_reranking(
    logradouro="Rua Oscar Freire",
    bairro="Jardins",
    cidade="São Paulo",
    uf="SP",
    cep="01426-001"
)
# Esperado: Score ~98-100%, confiança HIGH
```

### Exemplo 2: Busca Sem CEP
```python
buscar_com_reranking(
    logradouro="Rua das Flores",
    bairro="Centro",
    cidade="Porto Alegre",
    uf="RS"
)
# Esperado: Score ~85-95%, confiança HIGH/MEDIUM
```

### Exemplo 3: Com Typo (Fuzzy Matching)
```python
buscar_com_reranking(
    logradouro="Avenda Palista",  # Typo: Avenida Paulista
    bairro="Bela Vsta",           # Typo: Bela Vista
    cidade="Sao Paulo",           # Sem acento
    uf="SP"
)
# Esperado: Score ~80-90%, fuzzy match funciona!
```

### Exemplo 4: Teste Rápido com Endereço Aleatório
```python
# Pegar endereço da base e testar
sample = df_dne.sample(1).iloc[0]

buscar_com_reranking(
    logradouro=sample['logradouro'],
    bairro=sample['bairro'],
    cidade=sample['cidade'],
    uf=sample['uf'],
    cep=sample['cep']
)
# Esperado: Score ~95-100%, deve retornar o próprio endereço
```

---

## 🎨 Modo Programático (Sem Print)

Para usar em scripts/APIs, desative o output:

```python
resultado = buscar_com_reranking(
    logradouro="Avenida Paulista",
    bairro="Bela Vista",
    cidade="São Paulo",
    uf="SP",
    cep="01310-100",
    verbose=False  # Desativa print
)

# Acessar dados estruturados
top_result = resultado['results'][0]
print(f"Score: {top_result['score']}")
print(f"Endereço: {top_result['address']['logradouro']}")
print(f"CEP: {top_result['address']['cep']}")
```

### Estrutura do JSON de Retorno:
```json
{
  "results": [
    {
      "address": {
        "logradouro": "Avenida Paulista",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "uf": "SP",
        "cep": "01310-100"
      },
      "score": 0.985,
      "raw_score": 1.182,
      "confidence": "high",
      "field_scores": {
        "logradouro": 0.987,
        "bairro": 0.901,
        "cidade": 0.995,
        "cep": 1.0
      },
      "num_fields_matched": 4
    }
  ],
  "query": { ... },
  "total_found": 5,
  "weights_used": { ... },
  "reranking_config": {
    "search_k": 500,
    "intersection_boost": 0.2
  }
}
```

---

## ⚙️ Configurações Avançadas

### Ajustar Precisão vs Performance

```python
# Mais precisão, mais lento (500+ candidatos)
resultado = buscar_com_reranking(
    ...,
    search_k=1000,           # Busca 1000 candidatos
    intersection_boost=0.3   # Boost maior (30%)
)

# Mais rápido, menos preciso (100-200 candidatos)
resultado = buscar_com_reranking(
    ...,
    search_k=200,           # Busca 200 candidatos
    intersection_boost=0.1  # Boost menor (10%)
)
```

**Padrão recomendado:**
- `search_k=500` → Balanço ideal
- `intersection_boost=0.2` → 20% boost

---

## ❓ FAQ

### Q: Quando usar CEP?
**A:** Sempre que disponível! CEP aumenta precisão em ~10-15%.

### Q: Score mínimo aceitável?
**A:**
- ✅ **≥ 80%** → Muito bom, use com confiança
- ⚠️ **60-80%** → Bom, mas valide resultado
- ❌ **< 60%** → Baixo, endereço pode estar errado ou não existir

### Q: Funciona com abreviações?
**A:** Sim! O sistema normaliza automaticamente:
- `R.` → `Rua`
- `Av.` → `Avenida`
- `Trav.` → `Travessa`
- etc.

### Q: Funciona com typos?
**A:** Sim! Busca vetorial tolera:
- Erros de digitação pequenos
- Acentos faltantes
- Espaços extras

### Q: Precisa de todos os campos?
**A:** Sim, todos são obrigatórios exceto CEP:
- logradouro ✅ obrigatório
- bairro ✅ obrigatório
- cidade ✅ obrigatório
- uf ✅ obrigatório
- cep ❌ opcional

### Q: Quão rápido é?
**A:**
- Com reranking: ~80-150ms por busca
- Sem reranking: ~30-50ms por busca
- Ainda muito rápido para produção!

---

## 🐛 Troubleshooting

### Erro: "search_engine_reranking não definido"
**Solução:** Execute todas as células anteriores do notebook até ver:
```
✅ SearchEngineWithReranking
✅ Ambos os sistemas prontos para comparação!
```

### Score muito baixo (<50%) mesmo com dados corretos
**Possíveis causas:**
1. Endereço não existe na base DNE
2. Normalização diferente (ex: "1º Andar" vs "Primeiro Andar")
3. Base de dados desatualizada

**Solução:** Verifique se o endereço existe manualmente:
```python
df_dne[df_dne['logradouro'].str.contains("termo da busca", case=False, na=False)]
```

### Latência muito alta (>500ms)
**Solução:** Reduza `search_k`:
```python
buscar_com_reranking(..., search_k=200)  # Ao invés de 500
```

---

## 📞 Suporte

Para questões ou problemas:
1. Verifique os exemplos no notebook
2. Execute células de diagnóstico (seção 9)
3. Consulte `SOLUCOES_PRECISAO.md` para detalhes técnicos

---

**Pronto! Agora você pode buscar endereços com alta precisão usando reranking! 🎉**
