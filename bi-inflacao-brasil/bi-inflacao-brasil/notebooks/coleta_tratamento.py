"""
Coleta, limpeza e organização das bases oficiais do projeto
"Dashboard de BI para Análise da Inflação no Brasil e seus Impactos no Poder de Compra".

Fontes (códigos verificados nas APIs oficiais em 12/11/2026):
  - IBGE/SIDRA Tab. 7060  IPCA mensal, ano, 12 meses e peso; índice geral, grupos e 16 áreas
  - IBGE/SIDRA Tab. 1737  IPCA número-índice (base dez/1993 = 100)
  - IBGE/SIDRA Tab. 1736  INPC número-índice e variação mensal (sensibilidade)
  - BCB/SGS 1619          Salário mínimo nominal vigente (R$)
  - BCB/SGS 433           IPCA variação mensal (validação cruzada)

Uso (Google Colab ou local):
    !pip install -r requirements.txt
    python notebooks/coleta_tratamento.py        # a partir da raiz do repositório

Saídas:
    dados/brutos/   respostas JSON originais das APIs (sem alteração)
    dados/tratados/ tabelas CSV limpas (modelo estrela) + log de qualidade
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# --------------------------------------------------------------------------
# Parâmetros do projeto
# --------------------------------------------------------------------------
INICIO, FIM = "202101", "202610"          # período de análise (70 meses)
INICIO_AUX = "202001"                     # início estendido p/ validar o acumulado em 12 meses
MES_BASE_REAL = "2026-10-01"              # mês-base do salário mínimo real

RAIZ = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
DIR_BRUTOS = RAIZ / "dados" / "brutos"
DIR_TRATADOS = RAIZ / "dados" / "tratados"

IBGE_API = "https://servicodados.ibge.gov.br/api/v3/agregados"
BCB_API = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

CAT_INDICE_GERAL = 7169
CAT_GRUPOS = [7170, 7445, 7486, 7558, 7625, 7660, 7712, 7766, 7786]

UF_MACRORREGIAO = {
    "AC": "Norte", "PA": "Norte", "MA": "Nordeste", "CE": "Nordeste", "PE": "Nordeste",
    "SE": "Nordeste", "BA": "Nordeste", "MG": "Sudeste", "ES": "Sudeste", "RJ": "Sudeste",
    "SP": "Sudeste", "PR": "Sul", "RS": "Sul", "MS": "Centro-Oeste", "GO": "Centro-Oeste",
    "DF": "Centro-Oeste",
}

# Símbolos especiais do IBGE para valor inexistente/indisponível/sigiloso
SIMBOLOS_AUSENTES = {"-", "..", "...", "X", "x", ""}

LOG: list[dict] = []


def registrar(codigo: str, descricao: str, ok: bool, detalhe: str = "") -> None:
    LOG.append({"codigo": codigo, "verificacao": descricao,
                "resultado": "OK" if ok else "FALHA", "detalhe": detalhe})
    print(f"[{'OK' if ok else 'FALHA'}] {codigo} {descricao} {detalhe}")


# --------------------------------------------------------------------------
# 1. COLETA
# --------------------------------------------------------------------------
def get_json(url: str, params: dict | None = None, tentativas: int = 4):
    for i in range(tentativas):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if i == tentativas - 1:
                raise
            print(f"  tentativa {i + 1} falhou ({e}); repetindo...")
            time.sleep(2 * (i + 1))


def salvar_bruto(nome: str, conteudo) -> None:
    DIR_BRUTOS.mkdir(parents=True, exist_ok=True)
    (DIR_BRUTOS / f"{nome}.json").write_text(
        json.dumps(conteudo, ensure_ascii=False, indent=1), encoding="utf-8")


def coletar_sidra(nome: str, tabela: int, inicio: str, fim: str, variaveis: list[int],
                  localidades: str, categorias: list[int] | None = None) -> pd.DataFrame:
    """Consulta a API de agregados do IBGE (v3) e devolve formato longo (valores ainda brutos)."""
    url = f"{IBGE_API}/{tabela}/periodos/{inicio}-{fim}/variaveis/{'|'.join(map(str, variaveis))}"
    params = {"localidades": localidades}
    if categorias:
        params["classificacao"] = f"315[{','.join(map(str, categorias))}]"
    dados = get_json(url, params)
    salvar_bruto(nome, dados)
    return sidra_para_longo(dados, tabela)


def sidra_para_longo(dados: list, tabela: int) -> pd.DataFrame:
    linhas = []
    for var in dados:
        for res in var["resultados"]:
            cat_id, cat_nome = None, None
            if res["classificacoes"]:
                (cat_id, cat_nome), = res["classificacoes"][0]["categoria"].items()
            for s in res["series"]:
                loc = s["localidade"]
                for periodo, valor in s["serie"].items():
                    linhas.append({
                        "tabela": tabela, "variavel_id": int(var["id"]), "variavel": var["variavel"],
                        "categoria_id": int(cat_id) if cat_id else None, "categoria": cat_nome,
                        "localidade_id": int(loc["id"]), "localidade": loc["nome"],
                        "nivel": loc["nivel"]["id"], "periodo": periodo, "valor_bruto": valor,
                    })
    return pd.DataFrame(linhas)


def coletar_sgs(nome: str, codigo: int, inicio: str = "01/12/2020", fim: str = "31/10/2026") -> pd.DataFrame:
    dados = get_json(BCB_API.format(codigo=codigo),
                     {"formato": "json", "dataInicial": inicio, "dataFinal": fim})
    salvar_bruto(nome, dados)
    df = pd.DataFrame(dados)
    df["serie_sgs"] = codigo
    return df


# --------------------------------------------------------------------------
# 2. LIMPEZA
# --------------------------------------------------------------------------
def limpar_sidra(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # 2.1 datas: AAAAMM -> primeiro dia do mês
    df["data"] = pd.to_datetime(df["periodo"], format="%Y%m")
    # 2.2 valores: símbolos especiais -> NaN (sem interpolação, RN-G08); texto -> número
    bruto = df["valor_bruto"].astype(str).str.strip()
    df["valor_ausente"] = bruto.isin(SIMBOLOS_AUSENTES)
    df["valor"] = pd.to_numeric(bruto.where(~df["valor_ausente"]).str.replace(",", "."), errors="coerce")
    # 2.3 nomes: remove numeração dos grupos ("1.Alimentação e bebidas" -> "Alimentação e bebidas")
    df["categoria"] = df["categoria"].str.replace(r"^\d+\.", "", regex=True).str.strip()
    # 2.4 áreas: "Fortaleza - CE" -> area_nome + uf
    partes = df["localidade"].str.rsplit(" - ", n=1, expand=True)
    df["area_nome"] = partes[0].str.strip()
    df["uf"] = partes[1].str.strip() if partes.shape[1] > 1 else None
    # 2.5 duplicatas exatas
    df = df.drop_duplicates(subset=["tabela", "variavel_id", "categoria_id", "localidade_id", "periodo"])
    return df


def limpar_sgs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"].astype(str).str.replace(",", "."), errors="coerce")
    return df.drop_duplicates(subset=["data"]).sort_values("data")


def pivotar(df: pd.DataFrame, chaves: list[str], nomes: dict[int, str]) -> pd.DataFrame:
    out = (df.pivot_table(index=chaves, columns="variavel_id", values="valor", aggfunc="first")
             .rename(columns=nomes).reset_index())
    out.columns.name = None
    return out


def no_periodo(df: pd.DataFrame, col: str = "data") -> pd.DataFrame:
    ini, fim = pd.to_datetime(INICIO, format="%Y%m"), pd.to_datetime(FIM, format="%Y%m")
    return df[(df[col] >= ini) & (df[col] <= fim)].reset_index(drop=True)


# --------------------------------------------------------------------------
# 3. CONSTRUÇÃO DAS TABELAS DO MODELO
# --------------------------------------------------------------------------
def acumulado_12m(serie_pct: pd.Series) -> pd.Series:
    """Produtório móvel de 12 meses (RN-G02)."""
    fator = 1 + serie_pct / 100
    return (fator.rolling(12).apply(np.prod, raw=True) - 1) * 100


def construir_calendario() -> pd.DataFrame:
    datas = pd.date_range(pd.to_datetime(INICIO, format="%Y%m"), pd.to_datetime(FIM, format="%Y%m"), freq="MS")
    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    return pd.DataFrame({
        "data": datas, "ano": datas.year, "mes_num": datas.month,
        "mes_nome": [meses[m - 1] for m in datas.month],
        "trimestre": "T" + datas.quarter.astype(str),
        "ano_mes": datas.strftime("%Y-%m"),
        "ano_completo": datas.year < 2026,
    })


def main() -> None:
    inicio_exec = datetime.now()
    print("== 1. COLETA ==")
    br_raw = coletar_sidra("sidra_7060_brasil_indice_geral", 7060, INICIO_AUX, FIM,
                           [63, 69, 2265], "N1[all]", [CAT_INDICE_GERAL])
    gr_raw = coletar_sidra("sidra_7060_brasil_grupos", 7060, INICIO, FIM,
                           [63, 66], "N1[all]", CAT_GRUPOS)
    ar_raw = coletar_sidra("sidra_7060_areas_indice_geral", 7060, INICIO, FIM,
                           [63, 2265], "N7[all]|N6[all]", [CAT_INDICE_GERAL])
    ni_raw = coletar_sidra("sidra_1737_ipca_numero_indice", 1737, "202012", FIM, [2266], "N1[all]")
    inpc_raw = coletar_sidra("sidra_1736_inpc", 1736, "202012", FIM, [2289, 44], "N1[all]")
    sm_raw = coletar_sgs("bcb_sgs_1619_salario_minimo", 1619)
    sgs433_raw = coletar_sgs("bcb_sgs_433_ipca_mensal", 433, "01/01/2021")

    print("== 2. LIMPEZA ==")
    br, gr, ar = limpar_sidra(br_raw), limpar_sidra(gr_raw), limpar_sidra(ar_raw)
    ni, inpc = limpar_sidra(ni_raw), limpar_sidra(inpc_raw)
    sm, sgs433 = limpar_sgs(sm_raw), limpar_sgs(sgs433_raw)
    for nome, d in [("Brasil", br), ("grupos", gr), ("áreas", ar), ("nº-índice", ni), ("INPC", inpc)]:
        n_aus = int(d["valor_ausente"].sum())
        registrar("QD-00", f"valores ausentes/símbolos especiais em {nome}", True, f"{n_aus} registro(s)")

    print("== 3. TABELAS ==")
    dcal = construir_calendario()

    # fIPCA_Brasil (12m também calculado por produtório, para validação)
    fbr = pivotar(br, ["data"], {63: "variacao_mensal_pct", 69: "variacao_ano_pct", 2265: "variacao_12m_pct"})
    fbr = fbr.sort_values("data")
    fbr["variacao_12m_calc_pct"] = acumulado_12m(fbr["variacao_mensal_pct"])
    fbr = fbr.merge(pivotar(ni, ["data"], {2266: "numero_indice"}), on="data", how="left")
    fbr = no_periodo(fbr)
    fbr["fonte"] = "IBGE/SIDRA Tab. 7060 e 1737"

    # dGrupo / fIPCA_Grupo
    dgr = (gr[["categoria_id", "categoria"]].drop_duplicates()
           .rename(columns={"categoria_id": "grupo_codigo", "categoria": "grupo_nome"})
           .sort_values("grupo_codigo").reset_index(drop=True))
    dgr["ordem_exibicao"] = range(1, len(dgr) + 1)
    fgr = pivotar(gr, ["data", "categoria_id"], {63: "variacao_mensal_pct", 66: "peso_mensal_pct"})
    fgr = fgr.rename(columns={"categoria_id": "grupo_codigo"})
    fgr["impacto_pp"] = fgr["peso_mensal_pct"] * fgr["variacao_mensal_pct"] / 100

    # dArea / fIPCA_Area
    dar = (ar[["localidade_id", "area_nome", "uf", "nivel"]].drop_duplicates()
           .rename(columns={"localidade_id": "area_codigo"}).reset_index(drop=True))
    dar["nivel"] = dar["nivel"].map({"N7": "Região Metropolitana", "N6": "Município"})
    dar["macrorregiao"] = dar["uf"].map(UF_MACRORREGIAO)
    dar["peso_regional_pct"] = np.nan  # preencher a partir do fascículo IPCA/INPC do IBGE (pendência)
    dar = pd.concat([pd.DataFrame([{"area_codigo": 1, "area_nome": "Brasil", "uf": None,
                                    "nivel": "Brasil", "macrorregiao": None, "peso_regional_pct": 100.0}]),
                     dar], ignore_index=True)
    far = pivotar(ar, ["data", "localidade_id"], {63: "variacao_mensal_pct", 2265: "variacao_12m_pct"})
    far = far.rename(columns={"localidade_id": "area_codigo"})

    # fSalarioMinimo (+ SM real e índice de poder de compra)
    fsm = no_periodo(sm[["data", "valor"]].rename(columns={"valor": "salario_minimo_nominal_rs"}))
    fsm = fsm.merge(fbr[["data", "numero_indice"]], on="data", how="left")
    base = fbr.loc[fbr["data"] == pd.Timestamp(MES_BASE_REAL), "numero_indice"].iloc[0]
    fsm["salario_minimo_real_rs"] = fsm["salario_minimo_nominal_rs"] * base / fsm["numero_indice"]
    p0 = fsm.iloc[0]
    fsm["indice_poder_compra"] = 100 * (fsm["salario_minimo_nominal_rs"] / p0["salario_minimo_nominal_rs"]) \
        / (fsm["numero_indice"] / p0["numero_indice"])
    fsm = fsm.drop(columns="numero_indice")
    fsm["fonte"] = "BCB/SGS 1619; deflator IBGE/SIDRA Tab. 1737"

    # fINPC_Brasil
    finpc = no_periodo(pivotar(inpc, ["data"], {2289: "numero_indice", 44: "variacao_mensal_pct"}))

    print("== 4. VALIDAÇÕES (QD) ==")
    n_meses = len(dcal)
    for nome, df, chave in [("fIPCA_Brasil", fbr, None), ("fIPCA_Grupo", fgr, "grupo_codigo"),
                            ("fIPCA_Area", far, "area_codigo"), ("fSalarioMinimo", fsm, None),
                            ("fINPC_Brasil", finpc, None)]:
        meses = df.groupby(chave)["data"].nunique() if chave else pd.Series([df["data"].nunique()])
        registrar("QD-01", f"{nome}: {n_meses} meses por chave", bool((meses == n_meses).all()),
                  f"mín={meses.min()} máx={meses.max()}")
        dup = df.duplicated(subset=["data"] + ([chave] if chave else [])).sum()
        registrar("QD-02", f"{nome}: sem chaves duplicadas", dup == 0, f"{dup} duplicada(s)")
        if dup:
            raise ValueError(f"Chaves duplicadas em {nome}")

    soma_pesos = fgr.groupby("data")["peso_mensal_pct"].sum()
    desvio = (soma_pesos - 100).abs().max()
    registrar("QD-03", "soma dos pesos dos 9 grupos = 100 (±0,01)", desvio <= 0.01, f"desvio máx={desvio:.4f}")

    soma_imp = fgr.groupby("data")["impacto_pp"].sum().rename("soma_impactos")
    comp = fbr.set_index("data")[["variacao_mensal_pct"]].join(soma_imp)
    dif = (comp["soma_impactos"] - comp["variacao_mensal_pct"]).abs()
    registrar("QD-04", "soma dos impactos ≈ IPCA do mês (±0,02 p.p.)", dif.max() <= 0.02,
              f"dif máx={dif.max():.3f} p.p. ({int((dif > 0.02).sum())} mês(es) acima)")

    dif12 = (fbr["variacao_12m_calc_pct"] - fbr["variacao_12m_pct"]).abs()
    registrar("QD-05", "12m por produtório = 12m publicado (±0,01 p.p.)", dif12.max() <= 0.01 + 1e-9,
              f"dif máx={dif12.max():.3f} p.p.")

    n_areas = far.groupby("data")["area_codigo"].nunique()
    registrar("QD-06", "16 áreas em todos os meses", bool((n_areas == 16).all()), f"mín={n_areas.min()}")

    mudancas = fsm.loc[fsm["salario_minimo_nominal_rs"].diff().fillna(0) != 0, "data"]
    fora_jan = [d.strftime("%Y-%m") for d in mudancas if d.month != 1]
    registrar("QD-07", "mudanças do SM só em janeiro (exceção esperada: 2023-05)",
              fora_jan in ([], ["2023-05"]), f"mudanças fora de jan: {fora_jan}")

    val433 = fbr.merge(no_periodo(sgs433[["data", "valor"]]), on="data", how="left")
    d433 = (val433["valor"] - val433["variacao_mensal_pct"]).abs().max()
    registrar("QD-09", "IPCA mensal IBGE = BCB/SGS 433", d433 <= 0.001, f"dif máx={d433:.3f}")

    print("== 5. EXPORTAÇÃO ==")
    DIR_TRATADOS.mkdir(parents=True, exist_ok=True)
    saidas = {"dCalendario": dcal, "dGrupo": dgr, "dArea": dar, "fIPCA_Brasil": fbr,
              "fIPCA_Grupo": fgr, "fIPCA_Area": far, "fSalarioMinimo": fsm, "fINPC_Brasil": finpc}
    for nome, df in saidas.items():
        df.to_csv(DIR_TRATADOS / f"{nome}.csv", index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
        print(f"  {nome}.csv  ({len(df)} linhas)")
    pd.DataFrame(LOG).to_csv(DIR_TRATADOS / "log_qualidade.csv", index=False, encoding="utf-8-sig")
    (DIR_TRATADOS / "metadados_extracao.json").write_text(json.dumps({
        "data_extracao": inicio_exec.isoformat(timespec="seconds"),
        "periodo": f"{INICIO}-{FIM}", "mes_base_salario_real": MES_BASE_REAL,
        "fontes": ["IBGE/SIDRA 7060", "IBGE/SIDRA 1737", "IBGE/SIDRA 1736", "BCB/SGS 1619", "BCB/SGS 433"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    falhas = [l for l in LOG if l["resultado"] == "FALHA"]
    print(f"\nConcluído. {len(falhas)} verificação(ões) com FALHA. Ver dados/tratados/log_qualidade.csv")


if __name__ == "__main__":
    main()
