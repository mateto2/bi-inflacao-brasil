# Catálogo das Fontes de Dados

**Projeto:** Dashboard de BI para Análise da Inflação no Brasil e seus Impactos no Poder de Compra
**Período coberto:** janeiro/2021 a outubro/2026
**Verificação:** em 12/11/2026, os códigos de tabelas, variáveis, categorias e localidades abaixo foram consultados diretamente nas APIs oficiais (metadados do IBGE e resposta da API do BCB).

Todas as fontes são públicas e oficiais, de acesso gratuito e sem cadastro.

---

## 1. Visão geral

| # | Instituição | Base / série | Uso no projeto | Perguntas |
|---|---|---|---|---|
| F1 | IBGE | SIDRA Tabela 7060: IPCA por índice geral, grupos e áreas | Principal | P1, P2, P3, P4 |
| F2 | IBGE | SIDRA Tabela 1737: IPCA série histórica com número-índice | Deflator e acumulados | P1, P5 |
| F3 | IBGE | SIDRA Tabela 1736: INPC série histórica com número-índice | Sensibilidade do salário real | P5 |
| F4 | Banco Central do Brasil | SGS série 1619: Salário mínimo | Principal (salário mínimo) | P5 |
| F5 | Banco Central do Brasil | SGS série 433: IPCA variação mensal | Validação cruzada | P1 |
| F6 | Ipea | Ipeadata MTE12_SALMIN12: Salário mínimo vigente | Validação histórica | P5 |
| F7 | IBGE | Fascículo mensal "Indicadores IBGE: IPCA e INPC" | Pesos regionais e notas metodológicas | P3 |

---

## 2. Fichas das fontes

### F1 — IBGE/SIDRA Tabela 7060

| Campo | Informação |
|---|---|
| Instituição | Instituto Brasileiro de Geografia e Estatística (IBGE) |
| Nome oficial | *IPCA - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (a partir de janeiro/2020)* |
| Consulta | https://sidra.ibge.gov.br/tabela/7060 |
| API (JSON) | `https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/{inicio}-{fim}/variaveis/{vars}?localidades={niveis}&classificacao=315[{categorias}]` |
| Metadados | https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados |
| Variáveis | 63 = Variação mensal (%); 69 = Variação acumulada no ano (%); 2265 = Variação acumulada em 12 meses (%); 66 = Peso mensal (%) |
| Classificação 315 | 7169 Índice geral; 7170 Alimentação e bebidas; 7445 Habitação; 7486 Artigos de residência; 7558 Vestuário; 7625 Transportes; 7660 Saúde e cuidados pessoais; 7712 Despesas pessoais; 7766 Educação; 7786 Comunicação (mais subgrupos, itens e subitens: 457 categorias no total) |
| Níveis territoriais | N1 Brasil; N7 Região Metropolitana; N6 Município |
| Periodicidade | Mensal |
| Cobertura temporal | 01/2020 a 10/2026 (conforme metadados em 12/11/2026) |
| Formatos | Interface web (exporta XLSX, CSV, ODS); API JSON |
| Perguntas atendidas | P1 (índice geral Brasil), P2 (grupos), P3 (áreas), P4 (série mensal) |

**Áreas de abrangência (16), com o código territorial do SIDRA:**

| Código | Área | Nível | Código | Área | Nível |
|---|---|---|---|---|---|
| 1501 | Belém - PA | RM | 4301 | Porto Alegre - RS | RM |
| 2301 | Fortaleza - CE | RM | 1200401 | Rio Branco - AC | Município |
| 2601 | Recife - PE | RM | 2111300 | São Luís - MA | Município |
| 2901 | Salvador - BA | RM | 2800308 | Aracaju - SE | Município |
| 3101 | Belo Horizonte - MG | RM | 5002704 | Campo Grande - MS | Município |
| 3201 | Grande Vitória - ES | RM | 5208707 | Goiânia - GO | Município |
| 3301 | Rio de Janeiro - RJ | RM | 5300108 | Brasília - DF | Município |
| 3501 | São Paulo - SP | RM | 4101 | Curitiba - PR | RM |

### F2 — IBGE/SIDRA Tabela 1737

| Campo | Informação |
|---|---|
| Nome oficial | *IPCA - Série histórica com número-índice, variação mensal e variações acumuladas em 3 meses, em 6 meses, no ano e em 12 meses (a partir de dezembro/1979)* |
| Consulta | https://sidra.ibge.gov.br/tabela/1737 |
| API | `https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/{inicio}-{fim}/variaveis/2266?localidades=N1[all]` |
| Variáveis | 2266 = Número-índice (base dez/1993 = 100); 63 = Variação mensal; 2263 = acum. 3 meses; 2264 = acum. 6 meses; 69 = acum. no ano; 2265 = acum. 12 meses |
| Nível | N1 Brasil |
| Periodicidade / cobertura | Mensal; 12/1979 a 10/2026 |
| Formatos | Web (XLSX/CSV); API JSON |
| Perguntas | P1 (acumulados), P5 (deflator do salário mínimo) |

### F3 — IBGE/SIDRA Tabela 1736

| Campo | Informação |
|---|---|
| Nome oficial | *INPC - Série histórica com número-índice, variação mensal e variações acumuladas em 3 meses, em 6 meses, no ano e em 12 meses (a partir de abril/1979)* |
| Consulta | https://sidra.ibge.gov.br/tabela/1736 |
| Variáveis | 2289 = Número-índice (base dez/1993 = 100); 44 = Variação mensal; 68 = acum. no ano; 2292 = acum. 12 meses |
| Nível | N1 Brasil |
| Periodicidade / cobertura | Mensal; 03/1979 a 10/2026 |
| Perguntas | P5 (análise de sensibilidade: deflator INPC) |

### F4 — Banco Central do Brasil, SGS 1619

| Campo | Informação |
|---|---|
| Nome | Salário mínimo (R$), Sistema Gerenciador de Séries Temporais |
| Consulta | https://www3.bcb.gov.br/sgspub (pesquisar pelo código 1619) |
| API | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.1619/dados?formato=json&dataInicial=01/12/2020&dataFinal=31/10/2026` (também `formato=csv`) |
| Campos | `data` (dd/mm/aaaa), `valor` (R$) |
| Periodicidade | Mensal (valor vigente no mês) |
| Cobertura verificada | 71 observações de 12/2020 a 10/2026. Valores no período: R$ 1.100 (2021), R$ 1.212 (2022), R$ 1.302 (jan–abr/2023), R$ 1.320 (mai–dez/2023), R$ 1.412 (2024), R$ 1.518 (2025), R$ 1.621 (2026) |
| Formatos | JSON, CSV (API) |
| Perguntas | P5 |

### F5 — Banco Central do Brasil, SGS 433

| Campo | Informação |
|---|---|
| Nome | Índice nacional de preços ao consumidor-amplo (IPCA), variação mensal (%) |
| API | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/2021` |
| Uso | Validação cruzada do IPCA mensal do IBGE (verificação QD-09) |
| Perguntas | P1 |

### F6 — Ipeadata MTE12_SALMIN12

| Campo | Informação |
|---|---|
| Nome oficial | Salário mínimo vigente (nominal; não considera abonos) |
| Consulta | http://www.ipeadata.gov.br (série MTE12_SALMIN12) |
| API (OData) | `http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='MTE12_SALMIN12')` |
| Limitação | Os metadados indicam **última atualização em 30/06/2025**, o que não garante a cobertura de 2026. Por isso o projeto usa a série SGS 1619 como fonte principal e o Ipeadata só como conferência histórica. |

### F7 — IBGE, fascículo "Indicadores IBGE: IPCA e INPC"

| Campo | Informação |
|---|---|
| Consulta | https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html (aba Publicações) |
| Uso | Pesos regionais das 16 áreas (campo `peso_regional_pct` de `dArea`), notas metodológicas e textos de divulgação usados para explicar variações (RN-G10) |
| Formato | PDF |

---

## 3. Arquivos do repositório gerados a partir das fontes

| Arquivo | Pasta | Origem | Conteúdo |
|---|---|---|---|
| `sidra_7060_brasil_indice_geral.json` | dados/brutos | F1 | IPCA Brasil: variação mensal, no ano e em 12 meses (01/2020–10/2026) |
| `sidra_7060_brasil_grupos.json` | dados/brutos | F1 | 9 grupos: variação mensal e peso |
| `sidra_7060_areas_indice_geral.json` | dados/brutos | F1 | 16 áreas: variação mensal e em 12 meses |
| `sidra_1737_ipca_numero_indice.json` | dados/brutos | F2 | Número-índice do IPCA |
| `sidra_1736_inpc.json` | dados/brutos | F3 | Número-índice e variação do INPC |
| `bcb_sgs_1619_salario_minimo.json` | dados/brutos | F4 | Salário mínimo mensal |
| `bcb_sgs_433_ipca_mensal.json` | dados/brutos | F5 | IPCA mensal (validação) |
| `dCalendario.csv`, `dGrupo.csv`, `dArea.csv` | dados/tratados | derivados | Dimensões do modelo estrela |
| `fIPCA_Brasil.csv`, `fIPCA_Grupo.csv`, `fIPCA_Area.csv` | dados/tratados | F1, F2 | Fatos do IPCA |
| `fSalarioMinimo.csv`, `fINPC_Brasil.csv` | dados/tratados | F4, F2, F3 | Salário mínimo nominal, real e índice de poder de compra; INPC |
| `log_qualidade.csv`, `metadados_extracao.json` | dados/tratados | pipeline | Resultado das verificações e data da extração |

Os arquivos de dados são gerados pelo notebook `notebooks/01_coleta_tratamento.ipynb` (ou pelo script `notebooks/coleta_tratamento.py`).
