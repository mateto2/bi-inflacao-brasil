# 1. Indicadores de Dados

**Projeto:** Dashboard de BI para Análise da Inflação no Brasil e seus Impactos no Poder de Compra
**Equipe:** Matheus Amaral, Tasso Tanouss e Aloísio Aragão
**Período de análise:** janeiro/2021 a outubro/2026
**Versão:** 1.1 — 12/11/2026 (códigos verificados nas APIs oficiais)

---

## 1.1 Convenções adotadas

| Símbolo | Significado |
|---|---|
| `t` | Mês de referência (AAAA-MM) |
| `I_t` | Número-índice do IPCA no mês `t` (base dez/1993 = 100) |
| `v_t` | Variação mensal do IPCA no mês `t`, em % |
| `g` | Grupo de produtos e serviços do IPCA (9 grupos) |
| `r` | Área geográfica de abrangência do IPCA (16 áreas) |
| `w_g,t` | Peso mensal do grupo `g` no mês `t`, em % |
| `Π` | Produtório (multiplicação encadeada) |

**Regra geral de agregação temporal:** variações percentuais de índices de preços **não se somam**. Para acumular duas ou mais variações mensais, usamos o produto dos fatores:

```
Variação acumulada (%) = [ Π (1 + v_t / 100) − 1 ] × 100
```

De forma equivalente, a variação acumulada também pode ser obtida pela razão entre números-índices: `(I_fim / I_início-1 − 1) × 100`.

**Fonte primária:** IBGE (Sistema Nacional de Índices de Preços ao Consumidor — SNIPC), via banco de tabelas SIDRA. As séries do Banco Central (SGS) e do Ipeadata servem como fontes complementares e de validação cruzada. O catálogo completo das fontes, com links verificados, será apresentado na Seção 3 (Etapa 3).

**Estrutura de ponderação:** desde janeiro de 2020, o IPCA usa pesos derivados da POF 2017-2018. Todo o período de análise (2021–2026) está, portanto, sob a mesma estrutura, o que permite comparar os grupos ao longo do tempo sem quebra metodológica.

---

## 1.2 Quadro-resumo dos indicadores

| # | Indicador | Unidade | Periodicidade | Fonte principal | Pergunta de negócio |
|---|---|---|---|---|---|
| I1 | IPCA mensal | % a.m. | Mensal | IBGE/SIDRA — Tab. 7060 (Brasil) | P1, P4 |
| I2 | IPCA acumulado em 12 meses | % | Mensal (janela móvel) | IBGE/SIDRA — Tab. 7060; validação: BCB/SGS 433 | P1, P5 |
| I3 | Variação do IPCA por grupo | % e p.p. | Mensal | IBGE/SIDRA — Tab. 7060 (classificação por grupos) | P2 |
| I4 | Inflação por área geográfica | % | Mensal | IBGE/SIDRA — Tab. 7060 (níveis RM e município) | P3 |
| I5 | Sazonalidade mensal e trimestral | % | Mensal / Trimestral | Derivado de I1 | P4 |
| I6 | Salário mínimo nominal e real | R$ | Mensal | BCB/SGS 1619 (validação: Ipeadata MTE12_SALMIN12); deflator: IPCA, SIDRA Tab. 1737 | P5 |

**Indicadores auxiliares** (usados no cálculo dos principais, sem visual próprio obrigatório): número-índice do IPCA (`I_t`), peso mensal por grupo (`w_g,t`), peso regional (`w_r`), IPCA acumulado no ano e INPC (para análise de sensibilidade do I6).

---

## 1.3 Especificação técnica detalhada

### I1 — IPCA mensal

| Atributo | Especificação |
|---|---|
| **Objetivo de negócio** | Medir a velocidade da inflação mês a mês e identificar episódios de aceleração, desaceleração ou deflação no período. |
| **Definição técnica** | Variação percentual do Índice Nacional de Preços ao Consumidor Amplo entre o mês de referência e o mês anterior, para o agregado Brasil. Mede a variação de preços da cesta de consumo de famílias com rendimento de 1 a 40 salários mínimos, residentes nas áreas urbanas cobertas pelo SNIPC. |
| **Fórmula** | `v_t = (I_t / I_t−1 − 1) × 100`. O valor é publicado diretamente pelo IBGE e é importado, não recalculado. O cálculo pelo número-índice serve apenas para validação. |
| **Unidade** | % ao mês, com 2 casas decimais (padrão de divulgação do IBGE). |
| **Periodicidade** | Mensal. |
| **Fonte** | IBGE/SIDRA, Tabela 7060, nível Brasil (N1), variável 63, classificação 315, categoria 7169 ("Índice geral"). Série longa e número-índice: Tabela 1737 (variáveis 63 e 2266). Validação: BCB/SGS, série 433. |
| **Campos necessários** | `mes_ref` (AAAA-MM), `localidade` (= Brasil), `categoria` (= Índice geral), `variacao_mensal_pct`. |
| **Visualização no Power BI** | Gráfico de colunas por mês, com cor condicional (valores negativos destacados como deflação). Cartão KPI com o último mês disponível e a variação em p.p. em relação ao mês anterior. |

### I2 — IPCA acumulado em 12 meses

| Atributo | Especificação |
|---|---|
| **Objetivo de negócio** | Expressar a inflação "anualizada" de cada mês, eliminando o efeito sazonal de meses isolados. É a medida usada para comparar com a meta de inflação e com reajustes salariais. |
| **Definição técnica** | Variação acumulada do IPCA nos 12 meses encerrados no mês `t`, inclusive. |
| **Fórmula** | `IPCA12m_t = [ Π_{k=0..11} (1 + v_t−k / 100) − 1 ] × 100`, ou, de forma equivalente, `(I_t / I_t−12 − 1) × 100`. **Variante derivada, para o período total:** `IPCA_período = [ Π_{t=jan/21..out/26} (1 + v_t / 100) − 1 ] × 100`. |
| **Unidade** | %, com 2 casas decimais. |
| **Periodicidade** | Mensal (janela móvel de 12 meses). |
| **Fonte** | Valor publicado em IBGE/SIDRA Tab. 7060, variável 2265 (variação acumulada em 12 meses). O cálculo próprio, a partir de I1 ou da série BCB/SGS 433, é usado como validação cruzada (tolerância de ±0,01 p.p. por arredondamento). |
| **Campos necessários** | `mes_ref`, `variacao_mensal_pct` (para cálculo) e `variacao_12m_pct` (valor publicado, para conferência). |
| **Visualização no Power BI** | Gráfico de linhas com o acumulado em 12 meses. A faixa de tolerância da meta de inflação (CMN) pode ser incluída opcionalmente como linhas de referência, com valores a confirmar na Etapa 3. Combinação recomendada: colunas para I1 e linha para I2 no eixo secundário. |
| **Observação** | O primeiro valor que pode ser calculado só com dados internos ao período é dez/2021. Para exibir o acumulado de jan/2021 a nov/2021, importa-se o valor publicado ou estende-se a extração da série mensal até fev/2020. |

### I3 — Variação do IPCA por grupo de produtos e serviços

| Atributo | Especificação |
|---|---|
| **Objetivo de negócio** | Identificar quais categorias de consumo mais encareceram e quais mais contribuíram para a inflação geral. |
| **Definição técnica** | Variação mensal de preços de cada um dos 9 grupos do IPCA: Alimentação e bebidas; Habitação; Artigos de residência; Vestuário; Transportes; Saúde e cuidados pessoais; Despesas pessoais; Educação; Comunicação. Cada grupo tem um peso mensal (`w_g,t`) que representa sua participação na cesta. |
| **Fórmulas** | **(a) Variação mensal do grupo:** `v_g,t`, publicada. **(b) Impacto (contribuição) no IPCA do mês:** `c_g,t = w_g,t × v_g,t / 100`, em pontos percentuais. Verificação: `Σ_g c_g,t ≈ v_t`, com diferenças residuais de arredondamento. **(c) Variação acumulada do grupo no período:** `[ Π_t (1 + v_g,t / 100) − 1 ] × 100`. |
| **Unidade** | `v_g,t` e acumulado: %. `c_g,t`: p.p. `w_g,t`: % da cesta. |
| **Periodicidade** | Mensal, com agregação para 12 meses, por ano e para o período total. |
| **Fonte** | IBGE/SIDRA, Tabela 7060, nível Brasil, classificação 315, categorias 7170, 7445, 7486, 7558, 7625, 7660, 7712, 7766 e 7786; variáveis 63 (variação mensal) e 66 (peso mensal). |
| **Campos necessários** | `mes_ref`, `grupo_codigo`, `grupo_nome`, `variacao_mensal_pct`, `peso_mensal_pct`. |
| **Visualização no Power BI** | (1) Barras horizontais ordenadas com a variação acumulada de cada grupo no período. (2) Gráfico de cascata (waterfall) com a contribuição em p.p. de cada grupo para o IPCA do mês ou do ano selecionado. (3) Treemap com os pesos dos grupos. (4) Segmentador de grupo. |
| **Regra crítica** | "Maior aumento de preço" (variação %) é diferente de "maior contribuição para a inflação" (impacto em p.p.). Um grupo de peso pequeno, como Educação, pode ter variação alta e impacto baixo. Os dois rankings devem ser apresentados separadamente. |

### I4 — Inflação por área geográfica ("região")

| Atributo | Especificação |
|---|---|
| **Objetivo de negócio** | Comparar a intensidade da inflação entre as localidades pesquisadas pelo IBGE e identificar onde o custo de vida subiu mais. |
| **Definição técnica** | Variação do IPCA em cada uma das **16 áreas** de abrangência do SNIPC, compostas por regiões metropolitanas, Distrito Federal e municípios: Belém, Fortaleza, Recife, Salvador, Belo Horizonte, Vitória (Grande Vitória), Rio de Janeiro, São Paulo, Curitiba, Porto Alegre, Brasília, Goiânia, Campo Grande, Rio Branco, São Luís e Aracaju. O índice Brasil é a média ponderada dos índices dessas áreas. |
| **Fórmulas** | **(a)** `v_r,t`, publicada. **(b)** Acumulado em 12 meses e no período: produtório, como em I2, aplicado a cada área. **(c)** Diferencial em relação ao Brasil: `Δ_r = Acum_r − Acum_Brasil`, em p.p. **(d)** Ranking das áreas pelo acumulado no período. |
| **Unidade** | % (variações) e p.p. (diferenciais). |
| **Periodicidade** | Mensal. |
| **Fonte** | IBGE/SIDRA, Tabela 7060, níveis Região Metropolitana (N7: 10 áreas) e Município (N6: 6 áreas), categoria 7169, variáveis 63 e 2265. O peso regional (`w_r`) vem das publicações mensais do IBGE (fascículo IPCA/INPC). |
| **Campos necessários** | `mes_ref`, `area_codigo`, `area_nome`, `uf`, `macrorregiao` (atributo derivado, para agrupamento), `variacao_mensal_pct`, `peso_regional_pct`. |
| **Visualização no Power BI** | (1) Barras ordenadas com o acumulado no período por área, mais uma linha de referência no valor do Brasil. (2) Mapa de pontos (bolhas) posicionado nas capitais, com tamanho ou cor proporcional ao acumulado. (3) Matriz de áreas × anos com formatação condicional. |
| **Regra crítica** | O IPCA **não** é publicado por macrorregião (Norte, Nordeste etc.) nem por estado. O dashboard deve rotular os resultados como "áreas pesquisadas", e não usar mapa coroplético de estados, que sugeriria cobertura estadual inexistente. O agrupamento por macrorregião só é permitido como indicador derivado, identificado como "não oficial" e calculado como média ponderada pelos pesos regionais das áreas daquela macrorregião. |

### I5 — Sazonalidade mensal e trimestral

| Atributo | Especificação |
|---|---|
| **Objetivo de negócio** | Verificar se existem meses ou trimestres em que a inflação tende a ser mais alta, como reajustes de início de ano, mensalidades escolares em fevereiro ou choques de energia. |
| **Definição técnica** | Perfil médio da inflação mensal por mês-calendário e por trimestre-calendário, calculado sobre os anos do período de análise. |
| **Fórmulas** | **Mensal:** `Sazon_m = média_{anos a} (v_{a,m})` para cada mês-calendário `m` = 1..12. A mediana é reportada como medida robusta complementar. **Trimestral:** primeiro, `v_{a,q} = [ Π_{t∈q} (1 + v_t / 100) − 1 ] × 100`; depois, `Sazon_q = média_{anos a} (v_{a,q})`. |
| **Unidade** | % (média da variação do mês ou do trimestre). |
| **Periodicidade** | Agregação de série mensal por mês e por trimestre-calendário. |
| **Fonte** | Derivado de I1 (IBGE/SIDRA Tab. 7060). Opcionalmente, também de I3, para a sazonalidade por grupo. |
| **Campos necessários** | `mes_ref`, `ano`, `mes_num`, `trimestre`, `variacao_mensal_pct`, mais uma tabela calendário (`dCalendario`). |
| **Visualização no Power BI** | (1) Colunas com a média por mês-calendário. (2) Mapa de calor (matriz ano × mês com formatação condicional). (3) Colunas com a média por trimestre. |
| **Regras críticas** | (a) Nº de observações por mês: jan–out têm 6 anos (2021–2026); nov–dez têm 5 anos (2021–2025). (b) O 4º trimestre de 2026 é incompleto e fica **excluído** da média trimestral. (c) Uma série de 5–6 anos não permite decomposição sazonal estatística formal, como X-13 ou STL. O indicador é descritivo, um "padrão médio observado", e deve ser apresentado como tal. (d) Os anos de 2021–2022, de inflação elevada, influenciam as médias, por isso a mediana é exibida junto. |

### I6 — Salário mínimo nominal e real

| Atributo | Especificação |
|---|---|
| **Objetivo de negócio** | Avaliar se o salário mínimo preservou, ganhou ou perdeu poder de compra frente à inflação no período. |
| **Definição técnica** | **Nominal:** valor legal mensal do salário mínimo nacional vigente em cada mês, em R$ correntes. **Real:** valor nominal convertido em R$ constantes de um mês-base (out/2026) pelo IPCA, o que representa sua capacidade de compra a preços de out/2026. |
| **Fórmulas** | **(a) SM real:** `SM_real_t = SM_nom_t × (I_out/2026 / I_t)`. **(b) Índice de poder de compra (jan/2021 = 100):** `IPC_SM_t = 100 × (SM_nom_t / SM_nom_jan21) / (I_t / I_jan21)`. **(c) Ganho real do reajuste anual:** `GR_a = [ (1 + Δ%SM_a / 100) / (1 + IPCA_acum_12m_dez(a−1) / 100) − 1 ] × 100`, em que `Δ%SM_a` compara o último valor vigente no ano `a` com o último do ano anterior. Em 2023, isso compõe os dois reajustes do ano (R$ 1.212 → R$ 1.320). **(d) Variação real acumulada no período:** `(SM_real_out26 / SM_real_jan21 − 1) × 100`. |
| **Unidade** | R$ (nominal e real em R$ de out/2026), índice (base 100) e % (ganho real). |
| **Periodicidade** | Mensal. O valor nominal muda, em regra, em janeiro. **Exceção no período: 2023**, com R$ 1.302,00 de janeiro a abril e R$ 1.320,00 a partir de maio (verificado na série SGS 1619). O valor real varia todo mês. |
| **Fonte** | Salário mínimo: **BCB/SGS, série 1619**, fonte principal, atualizada até out/2026. Conferência cruzada: Ipeadata MTE12_SALMIN12, com valores idênticos nos 70 meses (verificação QD-10) e decretos de reajuste (ex.: Decreto nº 12.797/2025, que fixou R$ 1.621,00 para 2026). Deflator: número-índice do IPCA (IBGE/SIDRA, Tab. 1737, variável 2266). Sensibilidade: número-índice do INPC (Tab. 1736, variável 2289). |
| **Campos necessários** | `mes_ref`, `salario_minimo_nominal_rs`, `ipca_numero_indice`, mais o parâmetro `mes_base` (padrão out/2026). |
| **Visualização no Power BI** | (1) Gráfico de linhas com duas séries, nominal (degraus anuais) e real. (2) Cartões KPI com o SM nominal atual, o SM real atual e a variação real acumulada. (3) Colunas com o ganho real de cada reajuste anual. (4) Linha do índice de poder de compra (base 100). |
| **Regras críticas** | (a) O deflator padrão é o **IPCA**, por coerência com o restante do projeto. (b) Análise de sensibilidade com o **INPC**: o reajuste legal do salário mínimo usa o INPC, e esse índice mede a cesta de famílias com renda de 1 a 5 SM, mais próxima de quem recebe o mínimo. Divergências entre os dois resultados devem ser relatadas. (c) "Salário real" aqui é um conceito de poder de compra de uma cesta média. Não equivale a renda efetiva do trabalhador nem considera tributos ou benefícios. |

---

## 1.4 Medidas de referência para o Power BI (DAX)

Esboço das medidas principais, a ajustar aos nomes finais das tabelas do modelo:

```DAX
-- Fator mensal (coluna calculada na fato do IPCA)
Fator = 1 + fIPCA[variacao_mensal_pct] / 100

-- IPCA acumulado no período selecionado pelo filtro de datas
IPCA Acumulado % =
    ( PRODUCTX ( fIPCA, fIPCA[Fator] ) - 1 ) * 100

-- IPCA acumulado em 12 meses, encerrado no último mês do contexto
IPCA 12m % =
VAR UltimoMes = MAX ( dCalendario[Data] )
RETURN
    ( PRODUCTX (
        DATESINPERIOD ( dCalendario[Data], UltimoMes, -12, MONTH ),
        CALCULATE ( MAX ( fIPCA[Fator] ) )
    ) - 1 ) * 100

-- Impacto do grupo no IPCA do mês (p.p.)
Impacto p.p. =
    SUMX ( fIPCA_Grupo, fIPCA_Grupo[peso_mensal_pct] * fIPCA_Grupo[variacao_mensal_pct] / 100 )

-- Salário mínimo real (R$ do mês-base)
SM Real =
VAR IndiceBase = CALCULATE ( MAX ( fIPCA[ipca_numero_indice] ), dCalendario[AnoMes] = "2026-10" )
RETURN
    SUMX ( fSalario, fSalario[salario_minimo_nominal_rs] * IndiceBase / RELATED ( fIPCA[ipca_numero_indice] ) )
```

> Observação: todas as medidas devem usar uma tabela calendário marcada como tabela de datas. Como o grão é mensal, cada mês é representado pelo seu primeiro dia.

---

## 1.5 Situação de disponibilidade dos dados (em 12/11/2026)

| Indicador | Cobertura necessária | Situação | Observação |
|---|---|---|---|
| I1, I2, I3, I4 | jan/2021–out/2026 | Disponível na fonte | O IPCA de outubro/2026 foi divulgado pelo IBGE em 12/11/2026 (0,14% no mês; 4,63% em 12 meses). A próxima divulgação está prevista para 11/12/2026. |
| I5 | jan/2021–out/2026 | Disponível na fonte (derivado) | O 4º trimestre de 2026 está incompleto e é excluído da média trimestral. |
| I6 | jan/2021–out/2026 | Disponível na fonte (SGS 1619) | O SM de 2026 é de R$ 1.621,00 (Decreto nº 12.797/2025). Ipeadata MTE12_SALMIN12 com valores idênticos ao SGS 1619 (QD-10). |

> **Status de verificação (12/11/2026):** os códigos de tabelas, variáveis, categorias e áreas citados acima foram **conferidos diretamente nas APIs oficiais**. Os metadados da Tab. 7060 indicam cobertura de 01/2020 a 10/2026. A série SGS 1619 retornou 71 observações entre dez/2020 e out/2026. A extração completa e o tratamento são feitos pelo notebook do repositório (`notebooks/01_coleta_tratamento.ipynb`).
