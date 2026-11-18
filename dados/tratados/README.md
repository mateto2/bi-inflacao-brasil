# dados/tratados

Tabelas CSV limpas (UTF-8, separador vírgula, decimal ponto) no modelo estrela descrito em `documentacao/02_perguntas_regras_negocio.md`, Seção 2.3:

- Dimensões: `dCalendario.csv`, `dGrupo.csv`, `dArea.csv`
- Fatos: `fIPCA_Brasil.csv`, `fIPCA_Grupo.csv`, `fIPCA_Area.csv`, `fSalarioMinimo.csv`, `fINPC_Brasil.csv`
- Controle: `log_qualidade.csv`, `metadados_extracao.json`

Esta pasta é preenchida ao executar o notebook `notebooks/01_coleta_tratamento.ipynb`. No Power BI, importe os CSVs em *Obter dados → Texto/CSV*.
