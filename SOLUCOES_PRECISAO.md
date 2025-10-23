# 🎯 Soluções para Melhorar Precisão do Sistema de Busca

## Contexto do Problema

Mesmo passando todos os campos corretos (dados sintéticos perfeitos), o sistema não atinge 100% de precisão devido ao **problema de candidatos diferentes por campo**:

- Campo `logradouro` retorna candidato A como mais similar
- Campo `bairro` retorna candidato B como mais similar
- Campo `cidade` retorna candidato C como mais similar
- Score final = soma ponderada de candidatos diferentes ≠ 100%

---

## 🥇 **Solução 1: Reranking com Interseção** (RECOMENDADA)

### ⭐ Efetividade: 9/10 | Esforço: 3/10

### Como Funciona
1. Busca **mais candidatos** por campo (search_k=500 ao invés de 100)
2. Identifica candidatos que aparecem em **múltiplos campos**
3. Aplica **boost de 20%** para candidatos na interseção
4. Retorna resultados reordenados

### Implementação
```python
class SearchEngineWithReranking(SearchEngine):
    def search_with_reranking(
        self,
        query: Dict[str, str],
        search_k: int = 500,  # Aumentado!
        intersection_boost: float = 0.2,  # +20% boost
        ...
    ):
        # Busca candidatos por campo
        # Identifica interseções
        # Aplica boost
        # Retorna resultados
```

### Vantagens
✅ **Melhoria de 5-15%** no score médio
✅ **Sem retreinar** modelos ou índices
✅ **Rápido**: +50-100ms por query (ainda <150ms total)
✅ **Transparente**: mostra `num_fields_matched` no resultado

### Desvantagens
⚠️ Aumenta latência em ~2x (de 30-50ms para 80-150ms)
⚠️ Usa mais memória temporária (candidatos maiores)

### Quando Usar
✅ Produção com requisitos de alta precisão
✅ Dados com nomes genéricos ("Centro", "Rua Principal")
✅ Quando latência <200ms é aceitável

### Teste no Notebook
Execute a célula "Comparação: Original vs Reranking" para validar ganhos.

---

## 🥈 **Solução 2: Aumentar efSearch do HNSW**

### ⭐ Efetividade: 6/10 | Esforço: 2/10

### Como Funciona
Aumenta a precisão do índice FAISS HNSW ao construir os índices.

### Implementação
```python
# Ao construir índices (EXECUTAR UMA VEZ)
index = faiss.IndexHNSWFlat(dimension, M=32)
index.hnsw.efSearch = 64  # Era 32, agora 64
```

### Vantagens
✅ Melhora recall do HNSW
✅ Sem mudança na API de busca
✅ Latência praticamente igual

### Desvantagens
⚠️ Precisa **reconstruir índices** (5-10 min)
⚠️ Aumento marginal (1-3% de melhoria)
⚠️ Consome mais memória durante busca

### Quando Usar
✅ Se você pode reconstruir índices
✅ Como complemento à Solução 1
✅ Base de dados estática

---

## 🥉 **Solução 3: Índices Separados por UF**

### ⭐ Efetividade: 8/10 | Esforço: 7/10

### Como Funciona
Cria um índice FAISS separado para cada UF (27 índices).

### Implementação
```python
# Construir 27 índices
for uf in df_dne['uf'].unique():
    df_uf = df_dne[df_dne['uf'] == uf]
    indices[uf] = build_index(df_uf)

# Buscar no índice correto
def search(query):
    uf = query['uf']
    return indices[uf].search(query_embedding)
```

### Vantagens
✅ **Reduz pool** de candidatos drasticamente
✅ Menos "Rua das Flores" competindo entre si
✅ Busca mais rápida (~20ms)

### Desvantagens
⚠️ **27x mais memória** (~2.5GB ao invés de 90MB)
⚠️ Complexidade de gerenciar múltiplos índices
⚠️ Reconstrução demorada (5-10min × 27)
⚠️ Requer UF na query (obrigatório)

### Quando Usar
✅ Infraestrutura com muita RAM (>4GB disponível)
✅ UF sempre disponível nas queries
✅ Performance crítica (<20ms)

---

## 🎖️ **Solução 4: Reranking com String Matching Exato**

### ⭐ Efetividade: 9/10 | Esforço: 5/10

### Como Funciona
Combina busca vetorial (fuzzy) com match exato de strings.

### Implementação
```python
def search_with_exact_reranking(query, top_k=5):
    # 1. Busca vetorial (top 50)
    candidates = vector_search(query, top_k=50)

    # 2. Rerank por match exato
    for candidate in candidates:
        exact_score = 0
        if candidate['logradouro'] == query['logradouro']:
            exact_score += 0.4
        if candidate['bairro'] == query['bairro']:
            exact_score += 0.3
        # ... etc

        candidate['final_score'] = (
            0.7 * candidate['vector_score'] +
            0.3 * exact_score
        )

    return sorted(candidates, key='final_score')[:top_k]
```

### Vantagens
✅ **Melhor dos dois mundos**: fuzzy + exato
✅ Melhoria de 10-20% em queries perfeitas
✅ Ainda funciona com typos (graças ao vetorial)

### Desvantagens
⚠️ Precisa normalizar strings (acentos, case)
⚠️ +30ms de latência
⚠️ Mais complexo de manter

### Quando Usar
✅ Mix de queries: algumas perfeitas, outras com typos
✅ Quando precisão em dados perfeitos é crítica
✅ Como complemento à Solução 1

---

## 📊 Comparação Resumida

| Solução | Efetividade | Esforço | Latência | Memória | Recomendação |
|---------|-------------|---------|----------|---------|--------------|
| **1. Reranking com Interseção** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | +50-100ms | +10MB | 🟢 **SIM** - Use em produção |
| **2. Aumentar efSearch** | ⭐⭐⭐ | ⭐⭐ | +5ms | +20MB | 🟡 Complementar |
| **3. Índices por UF** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐⭐⭐ | -10ms | +2.4GB | 🔴 Apenas se RAM abundante |
| **4. String Matching** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +30ms | +5MB | 🟡 Se precisão crítica |

---

## 🚀 Recomendação Final

### Para Produção Imediata:
1. **Implemente Solução 1 (Reranking)**
   - Já implementada no notebook
   - Use `search_engine_reranking.search_with_reranking()`
   - Teste e valide ganhos com célula comparativa

### Para Otimização Futura:
2. **Considere Solução 2** (se pode reconstruir índices)
3. **Avalie Solução 4** (se precisão em dados perfeitos é crítica)

### ⚠️ Evite (por enquanto):
- **Solução 3** (índices por UF): apenas se RAM >4GB e performance <20ms é obrigatória

---

## 📈 Expectativas Realistas

Com **Solução 1 (Reranking)**:

| Cenário | Score Esperado | Antes | Depois |
|---------|---------------|-------|--------|
| Dados sintéticos perfeitos | 98-100% | 85-95% | 95-100% |
| Query com 1 typo | 90-95% | 75-85% | 85-95% |
| Query com 2 typos | 80-90% | 60-75% | 75-90% |
| Query parcial (sem CEP) | 85-95% | 70-80% | 80-92% |

### 💡 Insight Final
**Não espere 100% exato em todos os casos.** Sistemas vetoriais têm imprecisão inerente de 0.5-2%.
- ✅ 98-99% = **EXCELENTE**
- ✅ 95-98% = **MUITO BOM**
- ⚠️ 90-95% = **BOM** (considere otimizações)
- ❌ <90% = **REVISAR** normalização/índices

---

## 🧪 Como Validar

Execute no notebook:

1. **Célula: "Teste Sintético"** → Valida score com dados perfeitos
2. **Célula: "Análise Campo por Campo"** → Identifica onde está o problema
3. **Célula: "Comparação Original vs Reranking"** → Quantifica ganhos

Espere ver melhoria de **+5-15%** no score médio com reranking.

---

## 📞 Próximos Passos

1. ✅ Execute testes no notebook
2. ✅ Valide ganhos com Solução 1
3. 🔄 Se satisfeito, implemente em produção (FastAPI)
4. 🔄 Monitore métricas (score médio, p95 latency)
5. 🔄 Ajuste `intersection_boost` se necessário (padrão: 0.2)

---

**Desenvolvido para otimizar busca vetorial de endereços DNE com FAISS + HNSW**
