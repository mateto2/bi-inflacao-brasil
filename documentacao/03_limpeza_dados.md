# 3. Limpeza e Mineração dos Dados

**Projeto:** Dashboard de BI para Análise da Inflação no Brasil e seus Impactos no Poder de Compra
**Implementação:** `notebooks/01_coleta_tratamento.ipynb` (Python + Pandas, executável no Google Colab)
**Versão:** 1.0 — 12/11/2026

Esta seção descreve o método de coleta, limpeza, integração e mineração das bases oficiais, correspondente às etapas **I (Identifique fontes)**, **L (Limpe as bases)** e parte de **A (Analise os dados)** da metodologia DEILAS adotada pelo projeto.

---

## 3.1 Fluxo geral (pipeline)

```text
APIs oficiais (IBGE/SIDRA, BCB/SGS)
        │  1. COLETA: requisições HTTP com repetição automática
        ▼
dados/brutos/*.json     ← cópia fiel da resposta (nunca editada)
        │  2. LIMPEZA: tipos, datas, símbolos, nomes, duplicatas
        ▼
DataFrames padronizados (formato longo)
        │  3. TRANSFORMAÇÃO: pivotagem, recorte do período, campos derivados
        ▼
Modelo estrela (3 dimensões + 5 fatos)
        │  4. VALIDAÇÃO: verificações QD-01 a QD-10 → log
        ▼
dados/tratados/*.csv  ──►  Power BI
```

**Princípios:**
1. **Imutabilidade do dado bruto:** a resposta original das APIs é salva sem alteração, o que garante reprodutibilidade e auditoria.
2. **Reprodutibilidade:** todo o tratamento é feito por código versionado no GitHub, sem edição manual de planilhas.
3. **Rastreabilidade (RN-G09):** cada tabela tratada indica a fonte, e a data de extração fica em `metadados_extracao.json`.

---

## 3.2 Coleta

| Passo | Descrição |
|---|---|
| Acesso | Coleta automatizada via APIs JSON públicas: API de Agregados do IBGE (v3) e API de dados abertos do BCB (SGS). Não é usado *web scraping*. |
| Parâmetros | Tabelas, variáveis, categorias e localidades com os códigos listados em `fontes_dados.md`. Período de 01/2021 a 10/2026; o IPCA Brasil começa em 01/2020 para permitir validar o acumulado em 12 meses. |
| Robustez | Até 4 tentativas por requisição, com espera progressiva, e *timeout* de 60 s. |
| Saída | 7 arquivos JSON em `dados/brutos/`. |

---

## 3.3 Limpeza

| # | Problema tratado | Regra aplicada | Justificativa |
|---|---|---|---|
| L1 | Datas em formatos distintos (IBGE: `AAAAMM`; BCB: `dd/mm/aaaa`) | Conversão para data com o primeiro dia do mês de referência (`AAAA-MM-01`) | Chave única de tempo para relacionar com `dCalendario` |
| L2 | Valores numéricos recebidos como texto | Conversão para número decimal (ponto como separador no tratamento) | Permite cálculos e evita erros de tipo no Power BI |
| L3 | Símbolos especiais do IBGE (`-`, `..`, `...`, `X`) | Convertidos para nulo (NaN) e marcados em `valor_ausente` | **Sem interpolação (RN-G08):** não se cria dado inexistente |
| L4 | Nomes de grupo com numeração (`1.Alimentação e bebidas`) | Remoção do prefixo numérico | Padronização de rótulos no dashboard |
| L5 | Nome da área com UF embutida (`Fortaleza - CE`) | Separação em `area_nome` e `uf` | Permite agrupar por UF e macrorregião |
| L6 | Registros duplicados | Remoção de duplicatas exatas pela chave (tabela, variável, categoria, localidade, período) | Integridade das chaves |
| L7 | Dados fora do período de análise | Recorte para 01/2021–10/2026 depois dos cálculos que exigem histórico | Coerência com o escopo declarado |
| L8 | Precisão numérica | Valores mantidos com a precisão da fonte; arredondamento só na exibição (RN-G05) | Evita erro acumulado nos produtórios |

---

## 3.4 Transformação e integração

| # | Transformação | Resultado |
|---|---|---|
| T1 | Pivotagem do formato longo (uma linha por variável) para o formato largo (uma coluna por variável) | Tabelas fato com colunas nomeadas pelo dicionário de dados (Seção 2.3) |
| T2 | Integração IPCA × número-índice × salário mínimo pela chave `data` | `fSalarioMinimo` com o valor real calculado |
| T3 | Criação das dimensões `dCalendario`, `dGrupo`, `dArea` (com macrorregião derivada da UF) | Modelo estrela pronto para o Power BI |
| T4 | Campos derivados | `impacto_pp` (peso × variação / 100), `variacao_12m_calc_pct` (produtório móvel), `salario_minimo_real_rs` (R$ de out/2026), `indice_poder_compra` (jan/2021 = 100) |

---

## 3.5 Validação da qualidade

O pipeline registra o resultado de cada verificação em `dados/tratados/log_qualidade.csv`.

| Código | Verificação | Ação em caso de falha |
|---|---|---|
| QD-00 | Contagem de valores ausentes ou símbolos especiais | Registrar |
| QD-01 | 70 meses por chave em cada tabela fato | Registrar meses faltantes |
| QD-02 | Ausência de chaves duplicadas | **Interromper o pipeline** |
| QD-03 | Soma dos pesos dos 9 grupos = 100% (±0,01) | Registrar |
| QD-04 | Soma dos impactos dos grupos ≈ IPCA do mês (±0,02 p.p.) | Registrar |
| QD-05 | Acumulado 12 meses calculado = publicado (±0,01 p.p.) | Registrar; manter o valor publicado |
| QD-06 | 16 áreas presentes em todos os meses | Registrar |
| QD-07 | Mudanças do SM só em janeiro, com exceção conhecida em mai/2023 | Conferir com o decreto |
| QD-09 | IPCA mensal IBGE = IPCA mensal BCB/SGS 433 | Registrar |
| QD-10 | Salário mínimo BCB/SGS 1619 = Ipeadata MTE12_SALMIN12 | Registrar |

---

## 3.6 Mineração de dados (análise exploratória e descritiva)

As técnicas abaixo são as que o projeto aplica para extrair padrões das bases tratadas. Todas são **descritivas**, compatíveis com o tamanho da série (70 meses).

| Técnica | Aplicação | Pergunta |
|---|---|---|
| Agregação temporal por produtório | Acumulados no ano, em 12 meses e no período | P1, P2, P3 |
| Detecção de extremos | Máximo e mínimo do acumulado em 12 meses; meses de deflação | P1 |
| *Ranking* e decomposição | Ordenação dos grupos por variação acumulada e por contribuição (impacto em p.p.) | P2 |
| Análise comparativa (*benchmarking*) | Diferença de cada área em relação ao Brasil, em p.p. | P3 |
| Perfil sazonal descritivo | Média e mediana por mês e por trimestre-calendário; mapa de calor ano × mês | P4 |
| Deflacionamento e números-índice | Salário real, índice de poder de compra, ganho real por reajuste | P5 |
| Análise de sensibilidade | Salário real deflacionado por IPCA × INPC | P5 |

Não são aplicados modelos preditivos nem decomposição sazonal estatística (X-13, STL): a série é curta e o objetivo do dashboard é descritivo (ver limitações na Seção 2.5).

---

## 3.7 Execução

```bash
# Local
pip install -r requirements.txt
python notebooks/coleta_tratamento.py

# Google Colab
# abrir notebooks/01_coleta_tratamento.ipynb → Ambiente de execução → Executar tudo
```

**Situação em 12/11/2026:** o código foi escrito com base na estrutura real das respostas das APIs, conferida em consultas de amostra. Também passou por um teste ponta a ponta com respostas simuladas de mesma estrutura, com todas as verificações QD sem falha. Em 12/11/2026 o notebook foi executado no Google Colab com os dados oficiais: todas as verificações QD retornaram OK. Observação: os servidores do Colab ficam fora do Brasil e não acessam a API do IBGE (a conexão expira); por isso, no Colab, as requisições são feitas pelo navegador do usuário (função `get_json`).
