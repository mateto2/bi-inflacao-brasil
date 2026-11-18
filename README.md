# Dashboard de BI para Análise da Inflação no Brasil e seus Impactos no Poder de Compra

Projeto acadêmico de Business Intelligence que analisa a evolução da inflação brasileira (IPCA) de **janeiro/2021 a outubro/2026** e seu impacto no poder de compra, comparando a inflação com a evolução do salário mínimo.

**Equipe:** Tasso Tanouss · Matheus Amaral · Aloísio Aragão

---

## Objetivo

Desenvolver um dashboard de BI que consolide dados oficiais de inflação em uma visão única e permita identificar tendências, categorias e regiões críticas, períodos de maior pressão sobre os preços e a variação do poder de compra, apoiando o planejamento financeiro de consumidores e empresas.

## Perguntas de negócio

1. **Evolução:** como a inflação brasileira evoluiu nos últimos cinco anos?
2. **Categorias:** quais categorias de produtos e serviços apresentaram os maiores aumentos de preços?
3. **Regiões:** quais regiões (áreas pesquisadas pelo IBGE) registraram as maiores taxas de inflação?
4. **Sazonalidade:** quais períodos do ano apresentaram os maiores índices de inflação?
5. **Poder de compra:** como a inflação impactou o poder de compra em relação à evolução do salário mínimo?

## Indicadores

| # | Indicador | Fonte |
|---|---|---|
| I1 | IPCA mensal | IBGE/SIDRA 7060 |
| I2 | IPCA acumulado em 12 meses | IBGE/SIDRA 7060 e 1737 |
| I3 | Variação e impacto do IPCA por grupo | IBGE/SIDRA 7060 |
| I4 | Inflação por área geográfica (16 áreas) | IBGE/SIDRA 7060 |
| I5 | Sazonalidade mensal e trimestral | Derivado de I1 |
| I6 | Salário mínimo nominal e real | BCB/SGS 1619 + IBGE/SIDRA 1737 (deflator) |

## Tecnologias

- **Python + Pandas:** coleta, limpeza e tratamento dos dados
- **Google Colab:** ambiente de execução dos notebooks
- **Power BI:** modelagem (esquema estrela) e dashboard
- **GitHub:** controle de versão e repositório do projeto

## Fontes de dados

IBGE (SIDRA: tabelas 7060, 1737 e 1736), Banco Central do Brasil (SGS: séries 1619 e 433) e Ipeadata (MTE12_SALMIN12, para validação). Catálogo completo, com links e códigos verificados, em [`fontes_dados.md`](fontes_dados.md).

## Estrutura do repositório

```text
bi-inflacao-brasil/
├── dados/
│   ├── brutos/      # respostas originais das APIs (JSON)
│   └── tratados/    # tabelas limpas (CSV) para o Power BI
├── dashboard/
│   └── Dashboard_Inflacao.pbix      # dashboard Power BI (6 páginas)
├── documentacao/
│   ├── 01_indicadores.md
│   ├── 02_perguntas_regras_negocio.md
│   ├── 03_limpeza_dados.md
│   └── Documentacao_BI_Inflacao.docx
├── notebooks/
│   ├── 01_coleta_tratamento.ipynb   # notebook para o Google Colab
│   └── coleta_tratamento.py         # mesmo pipeline em script
├── README.md
├── fontes_dados.md
└── requirements.txt
```

## Como executar

```bash
git clone https://github.com/USUARIO/bi-inflacao-brasil.git
cd bi-inflacao-brasil
pip install -r requirements.txt
python notebooks/coleta_tratamento.py
```

No Google Colab: abra `notebooks/01_coleta_tratamento.ipynb` e use *Ambiente de execução → Executar tudo*. As tabelas tratadas são gravadas em `dados/tratados/`, e o resultado das verificações de qualidade fica em `dados/tratados/log_qualidade.csv`.

## Principais resultados (jan/2021–out/2026)

- Inflação acumulada (IPCA): **38,59%**. Pico em 12 meses de 12,13% (abr/2022).
- Maior aumento de preço: **Vestuário (+47,8%)**. Maior contribuição: **Alimentação e bebidas (7,5 p.p.)**.
- Maior inflação acumulada: **São Paulo (40,8%)**. Menor: **Porto Alegre (35,6%)**.
- Meses mais inflacionários: **fevereiro e março**. Menos inflacionário: **agosto**.
- Salário mínimo: +47,4% nominal, o que dá **ganho real de 6,6%**.

## Como abrir o dashboard

Abra `dashboard/Dashboard_Inflacao.pbix` no Power BI Desktop (gratuito). Para atualizar, use *Página Inicial → Atualizar*: os dados são lidos dos CSVs deste repositório.

## Metodologia (DEILAS)

**D**efina o objetivo → **E**stabeleça métricas → **I**dentifique fontes → **L**impe as bases → **A**nalise os dados → **S**ugira decisões.

## Status

| Etapa | Situação |
|---|---|
| Objetivo, problema e perguntas de negócio | Concluído |
| Indicadores e regras de negócio | Concluído (`documentacao/01` e `02`) |
| Fontes de dados identificadas e verificadas | Concluído (`fontes_dados.md`) |
| Método de limpeza e mineração | Concluído (`documentacao/03`) |
| Extração e tratamento dos dados | Executado no Colab em 12/11/2026 (todas as verificações OK) |
| Dashboard Power BI | Concluído (`dashboard/Dashboard_Inflacao.pbix`) |
| Resultados e sugestão de decisões | Concluído (Seção 4 do documento) |
