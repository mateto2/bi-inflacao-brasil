# 2. Perguntas de Negócio, Dados de Negócio e Regras de Negócio

**Projeto:** Dashboard de BI para Análise da Inflação no Brasil e seus Impactos no Poder de Compra
**Equipe:** Tasso Tanouss, Matheus Amaral e Aloísio Aragão
**Período de análise:** janeiro/2021 a outubro/2026 (70 meses)
**Versão:** 1.1 — 12/11/2026

Esta seção detalha as cinco perguntas de negócio da documentação original. Para cada uma, define os dados necessários, os indicadores (especificados na Seção 1), as regras de negócio, os filtros, o método de cálculo, o resultado esperado e a visualização. Em seguida vêm a especificação dos dados de negócio (dicionário de dados e modelo) e as limitações metodológicas.

> Os "resultados esperados" descrevem **a forma** da resposta que o dashboard entregará, e não valores. Nenhum número desta seção é resultado de análise: as conclusões só serão redigidas depois da extração e do tratamento dos dados oficiais.

---

## 2.1 Regras de negócio gerais (valem para todas as perguntas)

| Código | Regra |
|---|---|
| **RN-G01 — Período** | O recorte padrão é de jan/2021 a out/2026. A data de cada registro é o **mês de referência** do índice, e não a data de divulgação. |
| **RN-G02 — Acumulação** | Variações percentuais são acumuladas **somente por produtório**: `[Π(1 + v/100) − 1] × 100`. Somar ou tirar média de variações mensais para obter um acumulado é proibido. |
| **RN-G03 — Mensal × acumulado** | Toda medida exibida deve trazer o horizonte no rótulo: "no mês", "no ano", "em 12 meses" ou "no período". Inflação mensal e acumulada nunca dividem o mesmo eixo sem distinção visual (eixo secundário ou cor e legenda distintas). |
| **RN-G04 — Valor oficial** | Quando o IBGE publica o valor (variação mensal, no ano, em 12 meses), o dashboard usa o valor publicado. O cálculo próprio serve para validação; divergências acima de 0,01 p.p. são registradas no log de tratamento. |
| **RN-G05 — Precisão** | Os valores são armazenados com a precisão da fonte (variações com 2 casas, pesos com até 4 casas). O arredondamento ocorre apenas na exibição. |
| **RN-G06 — Cobertura geográfica** | O IPCA cobre 16 áreas (regiões metropolitanas, Distrito Federal e municípios). "Brasil" é o agregado oficial calculado pelo IBGE e não pode ser recalculado como média simples das áreas. |
| **RN-G07 — Estrutura de pesos** | Todo o período usa a estrutura de ponderação da POF 2017-2018, em vigor desde jan/2020. Por isso, não há quebra metodológica entre 2021 e 2026. |
| **RN-G08 — Dados ausentes** | Não há interpolação nem preenchimento artificial. Um mês sem dado fica em branco e é sinalizado no visual e no log. |
| **RN-G09 — Rastreabilidade** | Cada tabela tratada guarda a fonte, o código da tabela ou série e a data de extração. |
| **RN-G10 — Conclusões** | Só são permitidas afirmações sustentadas por um indicador calculado no dashboard. Simultaneidade temporal não deve ser apresentada como causa: atribuir a alta de um grupo a um evento exige fonte citada, como a nota de divulgação do IBGE. |

---

## 2.2 Detalhamento por pergunta

### P1 — Como a inflação brasileira evoluiu nos últimos cinco anos?

| Item | Especificação |
|---|---|
| **Objetivo da análise** | Descrever a trajetória da inflação no período: fases de aceleração e desaceleração, picos e vales, e a comparação entre anos. |
| **Dados necessários** | IPCA Brasil: variação mensal, variação acumulada no ano, variação acumulada em 12 meses e número-índice, de jan/2021 a out/2026. |
| **Indicadores relacionados** | I1 (IPCA mensal), I2 (IPCA 12 meses e acumulado do período). |
| **Regras de negócio** | **RN-P1-01:** a inflação anual de 2021 a 2025 é o acumulado de janeiro a dezembro (variação acumulada no ano publicada em dezembro, conferida por produtório). **RN-P1-02:** 2026 é ano parcial e aparece rotulado como "acumulado no ano até out/2026". A comparação com anos completos usa o acumulado em 12 meses. **RN-P1-03:** picos e vales são identificados na série de 12 meses (máximo e mínimo, com o mês), e não na série mensal, que é mais volátil. **RN-P1-04:** a faixa da meta de inflação é exibida opcionalmente, com os valores definidos pelo CMN para cada ano (a confirmar na Etapa 3). |
| **Filtros** | Ano; intervalo de meses; tipo de medida (no mês / no ano / em 12 meses). |
| **Método de cálculo** | Importar as variações publicadas. Calcular o acumulado do período por `Π(1 + v_t/100) − 1` (jan/21 a out/26). Localizar o máximo e o mínimo de `IPCA12m_t`. Montar a tabela anual com as variações de janeiro a dezembro. |
| **Resultado esperado** | (a) série mensal de 70 pontos; (b) inflação acumulada do período em um único valor; (c) maior e menor inflação em 12 meses, com os respectivos meses; (d) tabela de inflação anual 2021–2025, mais 2026 parcial. |
| **Visualização** | Gráfico combinado com colunas (no mês) e linha (12 meses, eixo secundário). Cartões KPI com o último mês, o 12 meses atual e o acumulado do período. Tabela anual. |

### P2 — Quais categorias apresentaram os maiores aumentos de preços?

| Item | Especificação |
|---|---|
| **Objetivo da análise** | Identificar os grupos de produtos e serviços com maior alta de preços e os que mais pesaram na inflação geral. |
| **Dados necessários** | Variação mensal e peso mensal dos 9 grupos do IPCA (nível Brasil). Opcionalmente, subgrupos e itens para detalhamento (drill-down). |
| **Indicadores relacionados** | I3 (variação, impacto e acumulado por grupo); I1 como referência. |
| **Regras de negócio** | **RN-P2-01:** "maior aumento de preço" é a maior **variação acumulada** do grupo no período selecionado, calculada por produtório. **RN-P2-02:** "maior contribuição para a inflação" é o maior **impacto**, `c_g,t = w_g,t × v_g,t / 100` (p.p.). Em janelas de mais de um mês, a contribuição é aproximada pela soma dos impactos mensais e rotulada como "aproximada". **RN-P2-03:** os pesos mudam mês a mês; usa-se sempre o peso do próprio mês, nunca um peso fixo. **RN-P2-04:** validação mensal com tolerância: a soma dos pesos dos 9 grupos deve ser 100% (±0,01) e a soma dos impactos deve ficar próxima do IPCA do mês (±0,02 p.p.). **RN-P2-05:** grupos só são comparados na mesma janela temporal. **RN-P2-06:** os grupos aparecem com a nomenclatura oficial do IBGE. **RN-P2-07:** os rankings de aumento e de contribuição são exibidos separadamente, porque podem divergir. |
| **Filtros** | Período; grupo; tipo de ranking (variação % / contribuição p.p.); área geográfica (opcional, se a extração incluir grupos por área). |
| **Método de cálculo** | Para cada grupo: acumulado no período por produtório; impacto mensal pelo peso × variação; ordenação decrescente nos dois critérios. |
| **Resultado esperado** | (a) ranking dos 9 grupos por variação acumulada; (b) ranking por contribuição; (c) evolução em 12 meses de cada grupo; (d) composição percentual da cesta (pesos). |
| **Visualização** | Barras horizontais ordenadas (variação acumulada). Cascata com a contribuição dos grupos para o IPCA do período. Linhas em pequenos múltiplos (12 meses por grupo). Treemap dos pesos. |

### P3 — Quais regiões registraram as maiores taxas de inflação?

| Item | Especificação |
|---|---|
| **Objetivo da análise** | Comparar a inflação entre as áreas pesquisadas pelo IBGE e identificar as de maior e menor alta acumulada. |
| **Dados necessários** | Variação mensal e acumulada em 12 meses do IPCA (índice geral) para as 16 áreas e para o Brasil; pesos regionais. |
| **Indicadores relacionados** | I4 (inflação por área); I2 como referência nacional. |
| **Regras de negócio** | **RN-P3-01:** a unidade de análise é a **área pesquisada**, com o nome oficial (ex.: "Fortaleza", referente à região metropolitana). **RN-P3-02:** é proibido extrapolar o resultado de uma área para o estado inteiro ou para a macrorregião. **RN-P3-03:** a agregação por macrorregião é opcional, calculada como média ponderada pelos pesos regionais e rotulada como "agregação não oficial, elaborada pela equipe". **RN-P3-04:** a classificação usa o acumulado no período e o acumulado em 12 meses do último mês. **RN-P3-05:** o IBGE não divulga margem de erro para o IPCA por área, então diferenças pequenas entre áreas devem ser interpretadas com cautela e não ser tratadas como diferenças relevantes sem ressalva. |
| **Filtros** | Período; área; macrorregião (atributo de agrupamento); medida (no período / em 12 meses). |
| **Método de cálculo** | Para cada área: produtório das variações mensais no período e diferença em relação ao Brasil (`Acum_r − Acum_Brasil`, em p.p.); ordenação. |
| **Resultado esperado** | (a) ranking das 16 áreas pelo acumulado no período; (b) diferença de cada área em relação ao Brasil; (c) evolução anual por área. |
| **Visualização** | Barras ordenadas com linha de referência no valor do Brasil. Mapa de pontos (bolhas) nas capitais. Matriz área × ano com formatação condicional. |

### P4 — Quais períodos do ano apresentaram os maiores índices de inflação?

| Item | Especificação |
|---|---|
| **Objetivo da análise** | Verificar se há meses ou trimestres do ano com inflação sistematicamente maior. |
| **Dados necessários** | IPCA Brasil mensal (jan/2021 a out/2026); calendário com mês e trimestre; opcionalmente, variação mensal por grupo. |
| **Indicadores relacionados** | I5 (sazonalidade), derivado de I1; I3 para sazonalidade por grupo (opcional). |
| **Regras de negócio** | **RN-P4-01:** o perfil mensal é a média, e também a mediana, da variação de cada mês-calendário entre os anos disponíveis. **RN-P4-02:** a inflação trimestral de cada ano vem do produtório dos três meses; o perfil trimestral é a média desses valores. **RN-P4-03:** o número de observações aparece no visual: jan–out com n = 6 (2021–2026), nov–dez com n = 5 (2021–2025). **RN-P4-04:** o 4º trimestre de 2026 está incompleto e fica fora do perfil trimestral. **RN-P4-05:** o "mês de maior inflação" é apresentado com média, mediana e n; se média e mediana apontarem meses diferentes, os dois resultados são relatados. **RN-P4-06:** o resultado é um padrão médio observado, sem decomposição sazonal estatística (a série é curta). |
| **Filtros** | Intervalo de anos; grupo (opcional); estatística (média / mediana). |
| **Método de cálculo** | Agrupar `v_t` por mês-calendário e calcular média e mediana. Calcular a variação trimestral por produtório e agrupar por trimestre-calendário. |
| **Resultado esperado** | (a) perfil dos 12 meses; (b) perfil dos 4 trimestres; (c) mapa de calor ano × mês que mostre a consistência do padrão ao longo dos anos. |
| **Visualização** | Colunas por mês-calendário (média, com marcador de mediana). Mapa de calor ano × mês. Colunas por trimestre. |

### P5 — Como a inflação impactou o poder de compra em relação à evolução do salário mínimo?

| Item | Especificação |
|---|---|
| **Objetivo da análise** | Medir se o salário mínimo ganhou, manteve ou perdeu poder de compra frente à inflação no período. |
| **Dados necessários** | Salário mínimo nominal vigente em cada mês; número-índice do IPCA; IPCA acumulado em 12 meses de dezembro; INPC (número-índice) para sensibilidade. |
| **Indicadores relacionados** | I6 (SM nominal e real, índice de poder de compra, ganho real); I2. |
| **Regras de negócio** | **RN-P5-01:** SM nominal é o valor legal vigente no mês, conforme o decreto de reajuste. **RN-P5-02:** o SM real é expresso em R$ de out/2026 (mês-base parametrizável): `SM_real_t = SM_nom_t × I_base / I_t`. **RN-P5-03:** o índice de poder de compra tem base jan/2021 = 100. Acima de 100 indica ganho de poder de compra; abaixo, perda. **RN-P5-04:** o ganho real do reajuste anual compara a variação do SM (último valor vigente no ano sobre o último do ano anterior) com o IPCA acumulado nos 12 meses até dezembro do ano anterior. Em 2023, os dois reajustes (jan e mai) são compostos. **RN-P5-05:** a comparação "inflação acumulada × reajuste acumulado" usa os mesmos meses de início e fim nas duas grandezas (jan/2021 a out/2026). **RN-P5-06:** o deflator padrão é o IPCA. O INPC entra como sensibilidade, porque é o índice da política de reajuste do mínimo e reflete famílias de 1 a 5 SM; divergências entre os dois são relatadas. **RN-P5-07:** o salário mínimo é uma referência normativa e não deve ser apresentado como renda média da população nem como renda efetiva do trabalhador. |
| **Filtros** | Período; deflator (parâmetro IPCA / INPC); mês-base do valor real. |
| **Método de cálculo** | Deflacionar o SM mês a mês pelo número-índice; calcular o índice de poder de compra, o ganho real de cada reajuste (2021 a 2026) e a variação real acumulada no período. |
| **Resultado esperado** | (a) séries do SM nominal (em degraus) e do SM real; (b) ganho ou perda real de cada reajuste anual; (c) variação real acumulada no período; (d) comparação entre os resultados com IPCA e com INPC. |
| **Visualização** | Linhas com SM nominal e real. Colunas com o ganho real por ano. Cartões KPI (SM atual, SM real, variação real acumulada). Linha do índice de poder de compra. |

---

## 2.3 Especificação dos dados de negócio

### 2.3.1 Modelo dimensional (esquema estrela)

```text
                 dCalendario
                      │ (data)
   ┌──────────┬───────┼──────────┬──────────────┐
fIPCA_Brasil fIPCA_Grupo  fIPCA_Area  fSalarioMinimo  fINPC_Brasil
                 │            │
              dGrupo        dArea
```

Granularidade de todas as tabelas fato: **mensal** (um registro por mês e por chave de dimensão).

### 2.3.2 Dicionário de dados

**dCalendario** — dimensão de tempo

| Campo | Tipo | Descrição / domínio |
|---|---|---|
| data | Data (PK) | Primeiro dia do mês de referência (01/01/2021 a 01/10/2026) |
| ano | Inteiro | 2021–2026 |
| mes_num | Inteiro | 1–12 |
| mes_nome | Texto | jan–dez |
| trimestre | Texto | T1–T4 |
| ano_mes | Texto | AAAA-MM |
| ano_completo | Booleano | Falso para 2026 (ano parcial) |

**dGrupo** — grupos do IPCA

| Campo | Tipo | Descrição / domínio |
|---|---|---|
| grupo_codigo | Inteiro (PK) | Código da categoria na classificação 315 do SIDRA (7170 a 7786, verificados na API) |
| grupo_nome | Texto | Nome oficial: Alimentação e bebidas; Habitação; Artigos de residência; Vestuário; Transportes; Saúde e cuidados pessoais; Despesas pessoais; Educação; Comunicação |
| ordem_exibicao | Inteiro | 1–9 |

**dArea** — áreas de abrangência do IPCA

| Campo | Tipo | Descrição / domínio |
|---|---|---|
| area_codigo | Inteiro (PK) | Código territorial do IBGE usado no SIDRA (ex.: 2301 = Fortaleza (RM); 5300108 = Brasília). A lista completa está em `fontes_dados.md` |
| area_nome | Texto | Nome oficial das 16 áreas, mais "Brasil" |
| nivel | Texto | Brasil / Região Metropolitana / Município |
| uf | Texto | Sigla da UF da área |
| macrorregiao | Texto | Norte, Nordeste, Centro-Oeste, Sudeste, Sul (atributo derivado, para agrupamento) |
| peso_regional_pct | Decimal | Peso da área no IPCA Brasil (%) |

**fIPCA_Brasil** — IPCA índice geral, Brasil

| Campo | Tipo | Descrição / regra |
|---|---|---|
| data | Data (FK) | Mês de referência |
| numero_indice | Decimal | Número-índice (base dez/1993 = 100) |
| variacao_mensal_pct | Decimal | % no mês (publicado) |
| variacao_ano_pct | Decimal | % acumulada no ano (publicado) |
| variacao_12m_pct | Decimal | % acumulada em 12 meses (publicado) |
| fonte / data_extracao | Texto / Data | Rastreabilidade (RN-G09) |

**fIPCA_Grupo** — IPCA por grupo, Brasil

| Campo | Tipo | Descrição / regra |
|---|---|---|
| data | Data (FK) | Mês de referência |
| grupo_codigo | Inteiro (FK) | → dGrupo |
| variacao_mensal_pct | Decimal | % no mês |
| peso_mensal_pct | Decimal | Peso do grupo no mês (%) |
| impacto_pp | Decimal (calculado) | `peso_mensal_pct × variacao_mensal_pct / 100` |

**fIPCA_Area** — IPCA índice geral por área

| Campo | Tipo | Descrição / regra |
|---|---|---|
| data | Data (FK) | Mês de referência |
| area_codigo | Inteiro (FK) | → dArea |
| variacao_mensal_pct | Decimal | % no mês |
| variacao_12m_pct | Decimal | % acumulada em 12 meses (publicado) |

**fSalarioMinimo** — salário mínimo nacional

| Campo | Tipo | Descrição / regra |
|---|---|---|
| data | Data (FK) | Mês de referência |
| salario_minimo_nominal_rs | Decimal | Valor legal vigente no mês (R$) |
| ato_normativo | Texto (opcional) | Decreto ou lei de referência do valor |

**fINPC_Brasil** — INPC índice geral, Brasil (sensibilidade da P5)

| Campo | Tipo | Descrição / regra |
|---|---|---|
| data | Data (FK) | Mês de referência |
| numero_indice | Decimal | Número-índice do INPC |
| variacao_mensal_pct | Decimal | % no mês |

### 2.3.3 Regras de qualidade dos dados (validação no tratamento em Python)

| Código | Verificação | Ação se falhar |
|---|---|---|
| QD-01 | Cada fato tem exatamente 70 meses (jan/2021–out/2026) por chave | Registrar meses faltantes; não interpolar |
| QD-02 | Sem chaves duplicadas (data + grupo/área) | Interromper o pipeline |
| QD-03 | Soma dos pesos dos 9 grupos = 100 ± 0,01 em cada mês | Registrar divergência |
| QD-04 | Soma dos impactos dos grupos ≈ IPCA do mês (±0,02 p.p.) | Registrar divergência |
| QD-05 | 12 meses calculado por produtório = 12 meses publicado (±0,01 p.p.) | Registrar divergência; manter o valor publicado |
| QD-06 | 16 áreas presentes em todos os meses | Registrar área ausente |
| QD-07 | SM nominal coincide com o valor legal; mudanças só em janeiro, **exceto 2023** (nova mudança em maio: R$ 1.302 → R$ 1.320) | Conferir com a fonte e o decreto |
| QD-08 | Valores numéricos com separador decimal padronizado (ponto no tratamento) | Converter |

---

## 2.4 Matriz de rastreabilidade

| Pergunta | Indicadores | Tabelas fato | Visual principal |
|---|---|---|---|
| P1 Evolução | I1, I2 | fIPCA_Brasil | Colunas + linha 12 meses |
| P2 Categorias | I3 | fIPCA_Grupo | Barras ordenadas + cascata |
| P3 Regiões | I4 | fIPCA_Area | Barras ordenadas + mapa de pontos |
| P4 Sazonalidade | I5 | fIPCA_Brasil (+ fIPCA_Grupo) | Mapa de calor ano × mês |
| P5 Poder de compra | I6, I2 | fSalarioMinimo, fIPCA_Brasil, fINPC_Brasil | Linhas nominal × real |

---

## 2.5 Limitações metodológicas

1. **População de referência:** o IPCA mede a inflação de famílias urbanas com renda de 1 a 40 salários mínimos nas 16 áreas pesquisadas. Não representa a inflação individual de cada família nem a de áreas rurais e cidades fora da amostra.
2. **Cobertura geográfica:** não há IPCA oficial por estado nem por macrorregião. Qualquer agregação desse tipo é elaboração da equipe.
3. **Ausência de margem de erro:** o IBGE não divulga intervalos de confiança para o IPCA, o que limita a interpretação de diferenças pequenas entre áreas e entre grupos.
4. **Período curto:** 70 meses permitem descrever padrões, mas não estimar sazonalidade de forma estatisticamente robusta. Os anos de 2021–2022, de inflação elevada, influenciam as médias.
5. **Ano parcial:** 2026 tem dados até outubro e não pode ser comparado diretamente com anos completos sem a ressalva.
6. **Contribuição acumulada aproximada:** a soma de impactos mensais é uma aproximação da contribuição de cada grupo em janelas longas.
7. **Salário mínimo × renda:** o mínimo é um piso legal. O poder de compra calculado refere-se a esse valor, e não à renda média dos trabalhadores, e não considera tributos, benefícios ou composição familiar.
8. **Escolha do deflator:** o resultado do salário real depende do índice usado (IPCA ou INPC). Por isso, ambos são apresentados.
9. **Causalidade:** o dashboard é descritivo. Associações temporais entre eventos e variações de preço não demonstram causa.
