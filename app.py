import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

IMPORT_CONFIG = {
    "credito_indevido_nao_tomador": {
        "groupby": ["ano", "mes"],
        "agg": {"qtd": "sum", "valor_base_icms": "sum", "valor_icms": "sum"},
    },
    "credito_indevido_repetido": {
        "groupby": ["ano", "mes"],
        "agg": {"qtd": "sum", "valor_base_icms": "sum", "valor_icms": "sum"},
    },
    "cte_emissor_saida_emitidos": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd_autorizada": "sum",
            "valor_autorizado": "sum",
        },
    },
    "cte_emissor_saida_nao_declarados_ou_valor_divergente": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "sum",
            "valor": "sum",
        },
    },
    "cte_emissor_saida_contingencia": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "sum",
            "percentual_autorizado": "sum",
        },
    },
    "cte_emissor_saida_cancelados": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "sum",
            "valor": "sum",
            "percentual": "sum",
        },
    },
    "cte_tomador_destinados_contribuinte": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd_autorizada": "sum",
            "valor": "sum",
        },
    },
    "cte_tomador_nao_declaradas_ou_divergente": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "sum",
            "valor_base_calculo": "sum",
            "valor_icms": "sum",
        },
    },
    "cte_tomador_nao_registradas_sitram": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "sum",
            "valor": "sum",
            "percentual": "sum",
        },
    },
    "debitos_fiscais": {
        "groupby": ["id"],
        "agg": {
            "vencimento": "first",
            "codigo": "first",
            "descricao": "first",
            "vencido": "first",
            "referencia": "first",
            "valor": "sum",
        },
    },
    "nf_entrada_autorizadas": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
            "percentual": "first",
        },
    },
    "nf_entrada_nao_declaradas": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
            "percentual": "first",
        },
    },
    "nf_entrada_divergentes": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
            "percentual": "first",
        },
    },
    "nf_entrada_nao_registradas_sitram": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
            "percentual": "first",
        },
    },
    "nf_entrada_discriminado": {
        "groupby": ["id"],
        "agg": {
            "chave_nfe": "first",
            "numero": "first",
            "emissao": "first",
            "valor": "first",
        },
    },
    "nf_saida_autorizadas": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nf_saida_nao_declaradas": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nf_saida_divergentes": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nf_saida_canceladas": {
        "groupby": ["ano", "mes", "tipo_operacao"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nf_saida": {
        "groupby": ["id"],
        "agg": {
            "chave_nfe": "first",
            "numero": "first",
            "emissao": "first",
            "valor": "first",
        },
    },
    "cfe_autorizadas": {
        "groupby": ["ano", "mes"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nfce_autorizadas": {
        "groupby": ["ano", "mes"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nfce_cfe_divergencias": {
        "groupby": ["ano", "mes"],
        "agg": {
            "valor": "first",
        },
    },
    "nfce_cfe_cancelados": {
        "groupby": ["ano", "mes"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nfce_cfe_ressalva": {
        "groupby": ["ano", "mes"],
        "agg": {
            "qtd": "first",
            "valor": "first",
        },
    },
    "nfce_cfe_discriminado": {
        "groupby": ["id"],
        "agg": {
            "chave_nfe": "first",
            "numero": "first",
            "emissao": "first",
            "valor": "first",
            "icms_destacado": "first",
        },
    },
    "pendencias_fiscais": {
        "groupby": ["id"],
        "agg": {
            "indicador": "first",
            "descricao": "first",
            "atualizacao": "first",
            "qtd": "first",
            "valor": "first",
        },
    },
    "metodo_pagamento": {
        "groupby": ["id"],
        "agg": {
            "entidade": "first",
            "mes": "first",
            "ano": "first",
            "valor": "first",
        },
    },
}

GET_CONFIG = {
    "cte": {
        "codi_esp": [38],
    },
    "nfe": {"codi_esp": [36, 37]},
    "nfce": {"codi_esp": [41]},
}


def get_and_proccess_table(table, cnpj):
    if table not in IMPORT_CONFIG:
        raise ValueError(f"Tabela '{table}' não configurada em IMPORT_CONFIG")

    conn = st.connection("postgres")
    df = conn.query(f"select * from {table} WHERE cnpj = '{cnpj}'")

    config = IMPORT_CONFIG[table]

    df_agg = (
        df.groupby(config["groupby"], as_index=False)
        .agg(config["agg"])
        .sort_values(config["groupby"])
    )

    return df_agg


def get_saida(emp, tipo):

    conn = st.connection("postgres")
    df = conn.query(
        """
    SELECT
        dsai_sai,
        vcon_sai,
        chave_nfe_sai,
        sigl_est,
        cancelada_sai
    FROM efsaidas
    WHERE codi_esp = ANY(:codi_esp)
      AND codi_emp = :emp
    """,
        params={"emp": emp, "codi_esp": GET_CONFIG[tipo]["codi_esp"]},
    )

    df["tipo"] = df["sigl_est"].apply(
        lambda uf: ("Oper. Interna" if uf == "CE" else "Interestadual")
    )
    df["valor"] = df["vcon_sai"]

    if len(df) > 0:
        df["ano"] = df["dsai_sai"].dt.year
        df["mes"] = df["dsai_sai"].dt.month
        df["dia"] = df["dsai_sai"].dt.day

    else:
        df["ano"] = ""
        df["mes"] = ""
        df["dia"] = ""

    df = df[["ano", "mes", "dia", "tipo", "valor", "chave_nfe_sai"]]

    return df


def get_ids_empresas():

    conn = st.connection("postgres")
    df = conn.query("SELECT codi_emp, nome_emp, esta_emp, cgce_emp FROM geempre")
    print(df)

    return df


def get_entrada(emp, tipo):

    conn = st.connection("postgres")
    df = conn.query(
        """
    SELECT
    dent_ent,
    vcon_ent,
    chave_nfe_ent
    FROM efentradas
    WHERE codi_esp =  ANY(:codi_esp)
    AND codi_emp = :emp
    """,
        params={"emp": emp, "codi_esp": GET_CONFIG[tipo]["codi_esp"]},
    )

    df["valor"] = df["vcon_ent"]

    if len(df) > 0:
        df["ano"] = df["dent_ent"].dt.year
        df["mes"] = df["dent_ent"].dt.month
        df["dia"] = df["dent_ent"].dt.day

    else:
        df["ano"] = ""
        df["mes"] = ""
        df["dia"] = ""

    df = df[["ano", "mes", "dia", "valor", "chave_nfe_ent"]]

    return df


def get_CFe(emp):

    conn = st.connection("postgres")
    df = conn.query(
        """
    SELECT
    data_cfe,
    valor_total_cfe,
    chave_cfe
    FROM efcupom_fiscal_eletronico
    WHERE codi_emp = :emp
    """,
        params={"emp": emp},
    )

    df["valor"] = df["valor_total_cfe"]

    if len(df) > 0:
        df["ano"] = df["data_cfe"].dt.year
        df["mes"] = df["data_cfe"].dt.month
        df["dia"] = df["data_cfe"].dt.day

    else:
        df["ano"] = ""
        df["mes"] = ""
        df["dia"] = ""

    df = df[["ano", "mes", "dia", "valor", "chave_cfe"]]

    return df


def filtrar_df(df, ano, tipo_operacao, mes):
    if tipo_operacao != "TODAS":
        df = df[(df["ano"] == ano) & (df["tipo_operacao"] == tipo_operacao)]
    else:
        df = df[df["ano"] == ano]

    if mes != "TODOS":
        df = df[df["mes"] == mes]

    return df


st.set_page_config(page_title="Felipe", initial_sidebar_state="expanded")


df_empresas = get_ids_empresas()
empresa = st.selectbox("ano", df_empresas["nome_emp"])
uf_empresa = df_empresas[df_empresas["nome_emp"] == empresa]["esta_emp"].iloc[0]
cod_empresa = df_empresas[df_empresas["nome_emp"] == empresa]["codi_emp"].iloc[0]
cnpj_empresa = df_empresas[df_empresas["nome_emp"] == empresa]["cgce_emp"].iloc[0]
ano = st.selectbox("ano", [2025, 2026])
tab = st.radio(
    "Selecione",
    [
        "CTe",
        "Débitos Fiscais",
        "Nf Entrada",
        "Nf Saída",
        "NFCe e CFe",
        "Pendências Fiscais",
        "Métodos de Pagamento",
    ],
    horizontal=True,
)


# ─────────────────────────────────────────────────────────
# Helpers visuais CTe
# ─────────────────────────────────────────────────────────
MESES_NOME = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

CTE_PALETTE = [
    "#4F8EF7", "#F76C6C", "#43C59E", "#F7B731",
    "#8854D0", "#2BCBBA", "#FC5C65", "#A55EEA",
]


def _safe_sum(df, col):
    """Soma segura: retorna 0 se coluna não existe ou df vazio."""
    if df is None or df.empty or col not in df.columns:
        return 0.0
    return pd.to_numeric(df[col], errors="coerce").fillna(0).sum()


def _safe_len(df):
    return 0 if df is None or df.empty else len(df)


def _fmt_brl(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ –"


def _bar_chart_mensal(df, col_valor, titulo, cor="#4F8EF7", key=None):
    """Gráfico de barras mensais seguro."""
    if df is None or df.empty or "mes" not in df.columns or col_valor not in df.columns:
        st.info("Sem dados para exibir no gráfico.")
        return
    df_plot = df.copy()
    df_plot[col_valor] = pd.to_numeric(df_plot[col_valor], errors="coerce").fillna(0)
    df_plot["Mês"] = df_plot["mes"].map(MESES_NOME).fillna(df_plot["mes"].astype(str))
    df_agg = df_plot.groupby("Mês", sort=False)[col_valor].sum().reset_index()
    # Ordena pelos meses do calendário
    ordem = [v for v in MESES_NOME.values() if v in df_agg["Mês"].values]
    df_agg["Mês"] = pd.Categorical(df_agg["Mês"], categories=ordem, ordered=True)
    df_agg = df_agg.sort_values("Mês")
    fig = px.bar(
        df_agg, x="Mês", y=col_valor,
        title=titulo,
        color_discrete_sequence=[cor],
        text_auto=True,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        title_font_size=14,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(showgrid=False),
    )
    fig.update_traces(marker_line_width=0, textfont_size=11)
    st.plotly_chart(fig, use_container_width=True, key=key)


def _metric_row(labels_values):
    """Renderiza uma linha de métricas estilizadas."""
    cols = st.columns(len(labels_values))
    for col, (label, val) in zip(cols, labels_values):
        col.metric(label=label, value=val)


def _painel_comparativo(
    df_sql: "pd.DataFrame",
    df_sefaz: "pd.DataFrame",
    col_val_sql: str,
    col_qtd_sefaz: str,
    col_val_sefaz: str,
    prefix: str,
):
    """
    Painel de comparação SQL Central x SEFAZ.
    Mostra:
      - Métricas de delta (diferença) globáis
      - Gráfico de barras agrupado por mês (valor)
      - Gráfico de barras agrupado por mês (qtd)
      - Tabela de divergência por mês
    """
    # ── Agrega SQL Central por mês ──────────────────────────
    if df_sql is not None and not df_sql.empty and "mes" in df_sql.columns:
        df_sql_agg = (
            df_sql.copy()
            .assign(**{col_val_sql: lambda d: pd.to_numeric(d[col_val_sql], errors="coerce").fillna(0)})
            .groupby("mes", as_index=False)
            .agg(sql_qtd=(col_val_sql, "count"), sql_valor=(col_val_sql, "sum"))
        )
    else:
        df_sql_agg = pd.DataFrame(columns=["mes", "sql_qtd", "sql_valor"])

    # ── Agrega SEFAZ por mês ───────────────────────────────
    if df_sefaz is not None and not df_sefaz.empty and "mes" in df_sefaz.columns:
        agg_spec = {}
        if col_qtd_sefaz and col_qtd_sefaz in df_sefaz.columns:
            df_sefaz = df_sefaz.assign(**{col_qtd_sefaz: pd.to_numeric(df_sefaz[col_qtd_sefaz], errors="coerce").fillna(0)})
            agg_spec["sefaz_qtd"] = (col_qtd_sefaz, "sum")
        if col_val_sefaz and col_val_sefaz in df_sefaz.columns:
            df_sefaz = df_sefaz.assign(**{col_val_sefaz: pd.to_numeric(df_sefaz[col_val_sefaz], errors="coerce").fillna(0)})
            agg_spec["sefaz_valor"] = (col_val_sefaz, "sum")
        if agg_spec:
            df_sefaz_agg = df_sefaz.groupby("mes", as_index=False).agg(**agg_spec)
        else:
            df_sefaz_agg = pd.DataFrame(columns=["mes"])
    else:
        df_sefaz_agg = pd.DataFrame(columns=["mes"])

    if "sefaz_qtd" not in df_sefaz_agg.columns:
        df_sefaz_agg["sefaz_qtd"] = 0
    if "sefaz_valor" not in df_sefaz_agg.columns:
        df_sefaz_agg["sefaz_valor"] = 0.0

    # ── Merge ───────────────────────────────────────────────
    todos_meses = sorted(
        set(df_sql_agg["mes"].tolist() if not df_sql_agg.empty else [])
        | set(df_sefaz_agg["mes"].tolist() if not df_sefaz_agg.empty else [])
    )
    if not todos_meses:
        st.info("⚠️ Nenhum dado disponível para comparar no período selecionado.")
        return

    df_comp = (
        pd.DataFrame({"mes": todos_meses})
        .merge(df_sql_agg,   on="mes", how="left")
        .merge(df_sefaz_agg, on="mes", how="left")
        .fillna(0)
    )
    df_comp["mes_nome"] = df_comp["mes"].map(MESES_NOME).fillna(df_comp["mes"].astype(str))
    df_comp["delta_valor"] = df_comp["sql_valor"] - df_comp["sefaz_valor"]
    df_comp["delta_qtd"]   = df_comp["sql_qtd"]   - df_comp["sefaz_qtd"]

    # ── Métricas globais de delta ───────────────────────────
    total_sql_val   = df_comp["sql_valor"].sum()
    total_sefaz_val = df_comp["sefaz_valor"].sum()
    total_sql_qtd   = df_comp["sql_qtd"].sum()
    total_sefaz_qtd = df_comp["sefaz_qtd"].sum()
    delta_val = total_sql_val - total_sefaz_val
    delta_qtd = total_sql_qtd - total_sefaz_qtd

    st.markdown("#### 🔄 Comparação SQL Central × SEFAZ")
    mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
    mc1.metric("SQL – Valor",   _fmt_brl(total_sql_val))
    mc2.metric("SEFAZ – Valor", _fmt_brl(total_sefaz_val))
    mc3.metric("Δ Valor",        _fmt_brl(delta_val),
               delta_color="inverse" if delta_val != 0 else "off")
    mc4.metric("SQL – Qtd",   int(total_sql_qtd))
    mc5.metric("SEFAZ – Qtd", int(total_sefaz_qtd))
    mc6.metric("Δ Qtd",        int(delta_qtd),
               delta_color="inverse" if delta_qtd != 0 else "off")

    st.markdown("")

    # ── Gráfico agrupado (valor) ─────────────────────────────
    fig_val = go.Figure()
    fig_val.add_trace(go.Bar(
        name="SQL Central", x=df_comp["mes_nome"], y=df_comp["sql_valor"],
        marker_color="#4F8EF7",
        text=df_comp["sql_valor"].apply(lambda v: _fmt_brl(v)),
        textposition="outside", textfont_size=10,
    ))
    fig_val.add_trace(go.Bar(
        name="SEFAZ", x=df_comp["mes_nome"], y=df_comp["sefaz_valor"],
        marker_color="#43C59E",
        text=df_comp["sefaz_valor"].apply(lambda v: _fmt_brl(v)),
        textposition="outside", textfont_size=10,
    ))
    fig_val.update_layout(
        barmode="group",
        title="Valor por Mês: SQL Central vs SEFAZ",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA", title_font_size=14,
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_val, use_container_width=True, key=f"{prefix}_comp_valor")

    # ── Gráfico agrupado (qtd) ───────────────────────────────
    fig_qtd = go.Figure()
    fig_qtd.add_trace(go.Bar(
        name="SQL Central", x=df_comp["mes_nome"], y=df_comp["sql_qtd"],
        marker_color="#8854D0",
        text=df_comp["sql_qtd"].astype(int),
        textposition="outside", textfont_size=10,
    ))
    fig_qtd.add_trace(go.Bar(
        name="SEFAZ", x=df_comp["mes_nome"], y=df_comp["sefaz_qtd"],
        marker_color="#F7B731",
        text=df_comp["sefaz_qtd"].astype(int),
        textposition="outside", textfont_size=10,
    ))
    fig_qtd.update_layout(
        barmode="group",
        title="Quantidade por Mês: SQL Central vs SEFAZ",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA", title_font_size=14,
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_qtd, use_container_width=True, key=f"{prefix}_comp_qtd")

    # ── Tabela de divergência por mês ──────────────────────
    st.markdown("##### 🔍 Divergência por Mês (SQL Central − SEFAZ)")
    df_div = df_comp[["mes_nome", "sql_qtd", "sefaz_qtd", "delta_qtd",
                       "sql_valor", "sefaz_valor", "delta_valor"]].copy()
    df_div = df_div.rename(columns={
        "mes_nome":    "Mês",
        "sql_qtd":     "Qtd SQL",
        "sefaz_qtd":   "Qtd SEFAZ",
        "delta_qtd":   "Δ Qtd",
        "sql_valor":   "Valor SQL (R$)",
        "sefaz_valor": "Valor SEFAZ (R$)",
        "delta_valor": "Δ Valor (R$)",
    })
    df_div["Qtd SQL"]       = df_div["Qtd SQL"].astype(int)
    df_div["Qtd SEFAZ"]     = df_div["Qtd SEFAZ"].astype(int)
    df_div["Δ Qtd"]         = df_div["Δ Qtd"].astype(int)

    def _style_delta(val):
        if isinstance(val, (int, float)):
            if val < 0:
                return "background-color: rgba(247,108,108,0.30); color:#ff6b6b; font-weight:600"
            elif val > 0:
                return "background-color: rgba(247,183,49,0.25); color:#f7b731; font-weight:600"
            else:
                return "background-color: rgba(67,197,158,0.20); color:#43c59e; font-weight:600"
        return ""

    styled = (
        df_div.style
        .applymap(_style_delta, subset=["Δ Qtd", "Δ Valor (R$)"])
        .format({
            "Valor SQL (R$)":   "{:,.2f}",
            "Valor SEFAZ (R$)": "{:,.2f}",
            "Δ Valor (R$)":     "{:,.2f}",
        })
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────
# Aba CTe
# ─────────────────────────────────────────────────────────
if tab == "CTe":

    st.markdown("## 📦 Conhecimento de Transporte Eletrônico (CTe)")
    st.markdown("---")

    subtab1, subtab2, subtab3 = st.tabs(
        ["🔴 Créditos Indevidos", "📤 Emissor", "📥 Tomador"]
    )

    # ── Créditos Indevidos ──────────────────────────────────
    with subtab1:
        df_cnt = get_and_proccess_table("credito_indevido_nao_tomador", cnpj_empresa)
        df_crep = get_and_proccess_table("credito_indevido_repetido", cnpj_empresa)

        # Filtro por ano (seguro)
        if not df_cnt.empty and "ano" in df_cnt.columns:
            df_cnt = df_cnt[df_cnt["ano"] == ano]
        if not df_crep.empty and "ano" in df_crep.columns:
            df_crep = df_crep[df_crep["ano"] == ano]

        # Métricas
        st.markdown("### 📊 Resumo de Créditos Indevidos")
        _metric_row([
            ("CTe Não-Tomador – Qtd",   int(_safe_sum(df_cnt,  "qtd"))),
            ("CTe Não-Tomador – Valor",  _fmt_brl(_safe_sum(df_cnt,  "valor_icms"))),
            ("CTe Repetidos – Qtd",      int(_safe_sum(df_crep, "qtd"))),
            ("CTe Repetidos – Valor",    _fmt_brl(_safe_sum(df_crep, "valor_icms"))),
        ])

        st.markdown("---")

        # Gráficos lado a lado
        gc1, gc2 = st.columns(2)
        with gc1:
            _bar_chart_mensal(
                df_cnt, "valor_icms",
                "Valor ICMS – CTe Não-Tomador", cor="#F76C6C", key="cte_ci_nao_tomador_valor"
            )
        with gc2:
            _bar_chart_mensal(
                df_crep, "valor_icms",
                "Valor ICMS – CTe Repetidos", cor="#F7B731", key="cte_ci_repetidos_valor"
            )

        st.markdown("---")

        # Tabelas
        st.markdown("#### CTe declarados onde o contribuinte NÃO é o tomador de serviço")
        if df_cnt.empty:
            st.info("Nenhum dado encontrado para o período selecionado.")
        else:
            st.dataframe(df_cnt, use_container_width=True, hide_index=True)

        st.markdown("#### CTe declarados REPETIDAMENTE na EFD")
        if df_crep.empty:
            st.info("Nenhum dado encontrado para o período selecionado.")
        else:
            st.dataframe(df_crep, use_container_width=True, hide_index=True)

    # ── Emissor ─────────────────────────────────────────────
    with subtab2:
        fe1, fe2 = st.columns(2)
        with fe1:
            tipo_emissor = st.selectbox(
                "Tipo de Operação",
                ["Oper. Interna", "Interestadual", "Do Exterior"],
                key="tipo_emissor",
            )
        with fe2:
            mes_emissor = st.selectbox(
                "Mês",
                ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                key="mes_emissor",
            )

        # ── Carga de dados ──────────────────────────────────
        # SQL Central (sistema interno)
        df_sql_emissor_full = get_saida(int(cod_empresa), "cte")
        df_sql_emissor = df_sql_emissor_full[df_sql_emissor_full["tipo"] == tipo_emissor].copy()
        if mes_emissor != "TODOS":
            df_sql_emissor = df_sql_emissor[df_sql_emissor["mes"] == mes_emissor]

        # SEFAZ
        TABELAS_EMISSOR = [
            ("Emitidos",                            "cte_emissor_saida_emitidos",                           "qtd_autorizada", "valor_autorizado"),
            ("Não Declarados / Valor Divergente",   "cte_emissor_saida_nao_declarados_ou_valor_divergente", "qtd",            "valor"),
            ("Emitidos em Contingência",            "cte_emissor_saida_contingencia",                       "qtd",            None),
            ("Cancelados",                          "cte_emissor_saida_cancelados",                         "qtd",            "valor"),
        ]
        dfs_emissor = {}
        for titulo, tabela, col_qtd, col_val in TABELAS_EMISSOR:
            df_t = get_and_proccess_table(tabela, cnpj_empresa)
            df_t = filtrar_df(df_t, ano, tipo_emissor, mes_emissor)
            dfs_emissor[titulo] = (df_t, col_qtd, col_val)

        df_emit = dfs_emissor["Emitidos"][0]
        df_ndiv = dfs_emissor["Não Declarados / Valor Divergente"][0]
        df_cont = dfs_emissor["Emitidos em Contingência"][0]
        df_canc = dfs_emissor["Cancelados"][0]

        # ── Seção 1: Painel Comparativo SQL × SEFAZ ─────────────
        st.markdown("### 🔄 Comparação SQL Central × SEFAZ (Emitidos)")
        st.caption(
            "Compara os CTe registrados no sistema interno (SQL Central) contra os "
            "CTe emitidos autorizados na base da SEFAZ, agrupados por mês."
        )
        _painel_comparativo(
            df_sql=df_sql_emissor,
            df_sefaz=df_emit,
            col_val_sql="valor",
            col_qtd_sefaz="qtd_autorizada",
            col_val_sefaz="valor_autorizado",
            prefix="emit",
        )

        st.markdown("---")

     

        # ── Seção 2: Tabelas brutas ───────────────────────
        st.markdown("### 🗂️ Dados Brutos")
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("#### 🏢 CTe SQL Central (ERP)")
            if df_sql_emissor.empty:
                st.info("Nenhum CTe encontrado no SQL Central para o filtro selecionado.")
            else:
                st.dataframe(df_sql_emissor, use_container_width=True, hide_index=True, height=500)
        with col2:
            for titulo, (df_t, _, _) in dfs_emissor.items():
                st.markdown(f"#### 📋 {titulo}")
                if df_t.empty:
                    st.info("Sem dados.")
                else:
                    st.dataframe(df_t, use_container_width=True, hide_index=True)
                st.markdown("")

    # ── Tomador ─────────────────────────────────────────────
    with subtab3:
        ft1, ft2 = st.columns(2)
        with ft1:
            tipo_tomador = st.selectbox(
                "Tipo de Operação",
                ["Oper. Interna", "Interestadual", "Do Exterior"],
                key="tipo_tomador",
            )
        with ft2:
            mes_tomador = st.selectbox(
                "Mês",
                ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                key="mes_tomador",
            )

        # ── Carga de dados ──────────────────────────────────
        df_sql_tomador = get_entrada(int(cod_empresa), "cte")
        if not df_sql_tomador.empty and mes_tomador != "TODOS":
            df_sql_tomador = df_sql_tomador[df_sql_tomador["mes"] == mes_tomador]

        TABELAS_TOMADOR = [
            ("Destinados ao Contribuinte",               "cte_tomador_destinados_contribuinte",      "qtd_autorizada", "valor"),
            ("Não Declarados / Valor Divergente na EFD", "cte_tomador_nao_declaradas_ou_divergente",  "qtd",           "valor_icms"),
            ("Com NFe não Registradas no SITRAM",        "cte_tomador_nao_registradas_sitram",        "qtd",           "valor"),
            ("Cancelados",                               "cte_emissor_saida_cancelados",              "qtd",           "valor"),
        ]
        dfs_tomador = {}
        for titulo, tabela, col_qtd, col_val in TABELAS_TOMADOR:
            df_t = get_and_proccess_table(tabela, cnpj_empresa)
            df_t = filtrar_df(df_t, ano, tipo_tomador, mes_tomador)
            dfs_tomador[titulo] = (df_t, col_qtd, col_val)

        df_dest   = dfs_tomador["Destinados ao Contribuinte"][0]
        df_ndivt  = dfs_tomador["Não Declarados / Valor Divergente na EFD"][0]
        df_sitram = dfs_tomador["Com NFe não Registradas no SITRAM"][0]
        df_canct  = dfs_tomador["Cancelados"][0]

        # ── Seção 1: Painel Comparativo SQL × SEFAZ ─────────────
        st.markdown("### 🔄 Comparação SQL Central × SEFAZ (Tomador)")
        st.caption(
            "Compara os CTe registrados como entrada no SQL Central contra os CTe "
            "destinados ao contribuinte na base da SEFAZ, agrupados por mês."
        )
        _painel_comparativo(
            df_sql=df_sql_tomador,
            df_sefaz=df_dest,
            col_val_sql="valor",
            col_qtd_sefaz="qtd_autorizada",
            col_val_sefaz="valor",
            prefix="tom",
        )

        st.markdown("---")

        # ── Seção 4: Tabelas brutas ───────────────────────
        st.markdown("### 🗂️ Dados Brutos")
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("#### 🏢 CTe SQL Central (ERP)")
            if df_sql_tomador.empty:
                st.info("Nenhum CTe encontrado no SQL Central para o filtro selecionado.")
            else:
                st.dataframe(df_sql_tomador, use_container_width=True, hide_index=True, height=500)
        with col2:
            for titulo, (df_t, _, _) in dfs_tomador.items():
                st.markdown(f"#### 📋 {titulo}")
                if df_t.empty:
                    st.info("Sem dados.")
                else:
                    st.dataframe(df_t, use_container_width=True, hide_index=True)
                st.markdown("")


if tab == "Débitos Fiscais":
    df_deb = get_and_proccess_table("debitos_fiscais", cnpj_empresa)

    # Garante colunas esperadas existam
    for _col in ["vencimento", "codigo", "descricao", "vencido", "referencia", "valor"]:
        if _col not in df_deb.columns:
            df_deb[_col] = None

    df_deb = df_deb[["vencimento", "codigo", "descricao", "vencido", "referencia", "valor"]].copy()
    df_deb["valor"] = pd.to_numeric(df_deb["valor"], errors="coerce").fillna(0)

    # ── Cabeçalho ──────────────────────────────────────────────
    st.markdown("## 💳 Débitos Fiscais")
    st.markdown("---")

    if df_deb.empty:
        st.info("Nenhum débito fiscal encontrado para este contribuinte.")
    else:
        # ── Classificação vencido / a vencer ───────────────────
        def _is_vencido(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, str):
                return v.strip().lower() in ("sim", "s", "true", "1", "vencido")
            return bool(v) if v is not None else False

        df_deb["_vencido_bool"] = df_deb["vencido"].apply(_is_vencido)

        total_valor    = df_deb["valor"].sum()
        valor_vencido  = df_deb.loc[df_deb["_vencido_bool"], "valor"].sum()
        valor_a_vencer = df_deb.loc[~df_deb["_vencido_bool"], "valor"].sum()
        qtd_total      = len(df_deb)
        qtd_vencidos   = int(df_deb["_vencido_bool"].sum())

        # ── Métricas ───────────────────────────────────────────
        st.markdown("### 📊 Resumo")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("💰 Total em Débito",   _fmt_brl(total_valor))
        mc2.metric("🔴 Vencido",           _fmt_brl(valor_vencido))
        mc3.metric("🟡 A Vencer",          _fmt_brl(valor_a_vencer))
        mc4.metric("📋 Qtd de Registros",  f"{qtd_total} ({qtd_vencidos} vencidos)")

        st.markdown("---")

        # ── Gráfico de barras por referência ───────────────────
        if "referencia" in df_deb.columns and df_deb["referencia"].notna().any():
            df_graf = (
                df_deb.groupby("referencia", as_index=False)["valor"]
                .sum()
                .sort_values("referencia")
            )
            # Colorir barra de acordo com: se há débitos vencidos naquela referência
            venc_por_ref = df_deb[df_deb["_vencido_bool"]].groupby("referencia")["valor"].sum().reset_index()
            venc_por_ref.columns = ["referencia", "valor_vencido"]
            df_graf = df_graf.merge(venc_por_ref, on="referencia", how="left").fillna(0)
            df_graf["cor"] = df_graf["valor_vencido"].apply(
                lambda v: "#F76C6C" if v > 0 else "#4F8EF7"
            )

            fig_deb = go.Figure()
            fig_deb.add_trace(go.Bar(
                name="Total",
                x=df_graf["referencia"].astype(str),
                y=df_graf["valor"],
                marker_color=df_graf["cor"].tolist(),
                text=df_graf["valor"].apply(_fmt_brl),
                textposition="outside",
                textfont_size=10,
            ))
            fig_deb.add_trace(go.Bar(
                name="Vencido",
                x=df_graf["referencia"].astype(str),
                y=df_graf["valor_vencido"],
                marker_color="rgba(247,108,108,0.45)",
                text=df_graf["valor_vencido"].apply(lambda v: _fmt_brl(v) if v > 0 else ""),
                textposition="inside",
                textfont_size=9,
            ))
            fig_deb.update_layout(
                barmode="overlay",
                title="Valor por Referência (🔴 vencido sobreposto)",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#FAFAFA",
                title_font_size=14,
                margin=dict(l=10, r=10, t=45, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                xaxis=dict(showgrid=False, title="Referência"),
            )
            st.plotly_chart(fig_deb, use_container_width=True, key="deb_fiscal_ref")
        else:
            st.info("Sem coluna 'referência' para gerar gráfico.")

        st.markdown("---")

        # ── Indicadores de alerta ──────────────────────────────
        if qtd_vencidos > 0:
            st.warning(
                f"⚠️ **{qtd_vencidos} débito(s) vencido(s)** totalizando **{_fmt_brl(valor_vencido)}**. "
                "Verifique urgência de regularização."
            )
        else:
            st.success("✅ Nenhum débito vencido identificado.")

        st.markdown("---")

        # ── Tabela estilizada ──────────────────────────────────
        st.markdown("### 🗂️ Detalhamento")

        df_exib = df_deb.drop(columns=["_vencido_bool"]).copy()

        def _style_vencido_row(row):
            cor_fundo = "rgba(247,108,108,0.18)" if _is_vencido(row["vencido"]) else ""
            return [f"background-color: {cor_fundo}" for _ in row]

        styled_deb = (
            df_exib.style
            .apply(_style_vencido_row, axis=1)
            .format({"valor": "{:,.2f}"})
        )
        st.dataframe(styled_deb, use_container_width=True, hide_index=True)

if tab == "Nf Entrada":
    st.markdown("## 📥 Nota Fiscal de Entrada")
    st.markdown("---")

    subtab1, subtab2 = st.tabs(["🔄 Comparativo & Agregado", "🔍 Discriminado"])

    # ── subtab1: Comparativo + Agregado ────────────────────────────────────
    with subtab1:
        f1, f2 = st.columns(2)
        with f1:
            tipo_nf_entrada = st.selectbox(
                "Tipo de Operação",
                ["Oper. Interna", "Interestadual", "Do Exterior"],
                key="tipo_nfe_ent",
            )
        with f2:
            mes_nf_entrada = st.selectbox(
                "Mês",
                ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                key="mes_nfe_ent",
            )

        # ── Carga ──────────────────────────────────────────────────────────
        df_sql_ent = get_entrada(int(cod_empresa), "nfe").copy()
        if not df_sql_ent.empty and mes_nf_entrada != "TODOS":
            df_sql_ent = df_sql_ent[df_sql_ent["mes"] == mes_nf_entrada]

        TABELAS_NFE_ENT = [
            ("Autorizadas",              "nf_entrada_autorizadas",             "qtd", "valor"),
            ("Não Declaradas na EFD",    "nf_entrada_nao_declaradas",          "qtd", "valor"),
            ("Valor Divergente na EFD",  "nf_entrada_divergentes",             "qtd", "valor"),
            ("Não Registradas SITRAM",   "nf_entrada_nao_registradas_sitram",  "qtd", "valor"),
        ]
        dfs_nfe_ent = {}
        for titulo, tabela, col_qtd, col_val in TABELAS_NFE_ENT:
            df_t = get_and_proccess_table(tabela, cnpj_empresa)
            df_t = filtrar_df(df_t, ano, tipo_nf_entrada, mes_nf_entrada)
            dfs_nfe_ent[titulo] = (df_t, col_qtd, col_val)

        df_aut   = dfs_nfe_ent["Autorizadas"][0]
        df_ndecl = dfs_nfe_ent["Não Declaradas na EFD"][0]
        df_divg  = dfs_nfe_ent["Valor Divergente na EFD"][0]
        df_sitr  = dfs_nfe_ent["Não Registradas SITRAM"][0]

        # ── Painel Comparativo SQL × SEFAZ ────────────────────────────────
        st.markdown("### 🔄 Comparação SQL Central × SEFAZ (Autorizadas)")
        st.caption(
            "Compara as NFe registradas como entrada no SQL Central contra as NFe "
            "autorizadas para o contribuinte na base da SEFAZ, agrupadas por mês."
        )
        _painel_comparativo(
            df_sql=df_sql_ent,
            df_sefaz=df_aut,
            col_val_sql="valor",
            col_qtd_sefaz="qtd",
            col_val_sefaz="valor",
            prefix="nfe_ent",
        )

        st.markdown("---")

        # ── Indicadores de Risco ──────────────────────────────────────────
        st.markdown("### ⚠️ Indicadores de Risco")
        ir1, ir2, ir3, ir4 = st.columns(4)
        ir1.metric(
            "🟥 Não Declaradas – Qtd", int(_safe_sum(df_ndecl, "qtd")),
            help="NFe autorizadas que não foram declaradas na EFD.",
        )
        ir2.metric("🟥 Não Declaradas – Valor", _fmt_brl(_safe_sum(df_ndecl, "valor")))
        ir3.metric(
            "🟡 Valor Divergente – Qtd", int(_safe_sum(df_divg, "qtd")),
            help="NFe declaradas com valor diferente na EFD.",
        )
        ir4.metric(
            "🟠 Não Reg. SITRAM – Qtd", int(_safe_sum(df_sitr, "qtd")),
            help="NFe não registradas no SITRAM.",
        )

        st.markdown("---")

        # ── Gráficos de detalhe ───────────────────────────────────────────
        st.markdown("### 📊 Detalhe por Categoria")
        gc1, gc2 = st.columns(2)
        with gc1:
            _bar_chart_mensal(df_ndecl, "valor", "Não Declaradas – Valor Mensal", cor="#F76C6C", key="nfe_ent_ndecl_val")
        with gc2:
            _bar_chart_mensal(df_divg,  "valor", "Valor Divergente – Valor Mensal", cor="#F7B731", key="nfe_ent_divg_val")

        gc3, gc4 = st.columns(2)
        with gc3:
            _bar_chart_mensal(df_ndecl, "qtd",   "Não Declaradas – Qtd Mensal",    cor="#FC5C65", key="nfe_ent_ndecl_qtd")
        with gc4:
            _bar_chart_mensal(df_sitr,  "valor",  "Não Reg. SITRAM – Valor Mensal", cor="#8854D0", key="nfe_ent_sitr_val")

        st.markdown("---")

        # ── Dados Brutos ──────────────────────────────────────────────────
        st.markdown("### 🗂️ Dados Brutos")
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("#### 🏢 NFe SQL Central (ERP)")
            if df_sql_ent.empty:
                st.info("Nenhuma NFe encontrada no SQL Central para o filtro selecionado.")
            else:
                st.dataframe(df_sql_ent, use_container_width=True, hide_index=True, height=450)
        with col2:
            for titulo, (df_t, _, _) in dfs_nfe_ent.items():
                st.markdown(f"#### 📋 {titulo}")
                if df_t.empty:
                    st.info("Sem dados.")
                else:
                    st.dataframe(df_t, use_container_width=True, hide_index=True)
                st.markdown("")

    # ── subtab2: Discriminado ──────────────────────────────────────────────
    with subtab2:
        st.markdown("### 🔍 NFe Discriminadas (nota a nota)")
        mes_nf_ent_disc = st.selectbox(
            "Mês",
            ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            key="mes_nfe_ent_disc",
        )

        # SQL Central
        df_sql_ent_disc = get_entrada(int(cod_empresa), "nfe").copy()
        if not df_sql_ent_disc.empty and mes_nf_ent_disc != "TODOS":
            df_sql_ent_disc = df_sql_ent_disc[df_sql_ent_disc["mes"] == mes_nf_ent_disc]

        # SEFAZ discriminado
        df_disc_sefaz = get_and_proccess_table("nf_entrada_discriminado", cnpj_empresa)
        if not df_disc_sefaz.empty and "emissao" in df_disc_sefaz.columns:
            df_disc_sefaz["ano"] = pd.to_datetime(df_disc_sefaz["emissao"], errors="coerce").dt.year
            df_disc_sefaz["mes"] = pd.to_datetime(df_disc_sefaz["emissao"], errors="coerce").dt.month
            df_disc_sefaz["dia"] = pd.to_datetime(df_disc_sefaz["emissao"], errors="coerce").dt.day
        else:
            for _c in ["ano", "mes", "dia"]:
                df_disc_sefaz[_c] = None

        if mes_nf_ent_disc != "TODOS" and not df_disc_sefaz.empty and "mes" in df_disc_sefaz.columns:
            df_disc_sefaz = df_disc_sefaz[df_disc_sefaz["mes"] == mes_nf_ent_disc]

        # Métricas rápidas
        _metric_row([
            ("SQL Central – Qtd",   _safe_len(df_sql_ent_disc)),
            ("SQL Central – Valor", _fmt_brl(_safe_sum(df_sql_ent_disc, "valor"))),
            ("SEFAZ – Qtd",         _safe_len(df_disc_sefaz)),
            ("SEFAZ – Valor",       _fmt_brl(_safe_sum(df_disc_sefaz, "valor"))),
        ])
        st.markdown("")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🏢 NFe SQL Central (ERP)")
            if df_sql_ent_disc.empty:
                st.info("Sem dados no SQL Central para este filtro.")
            else:
                st.dataframe(df_sql_ent_disc, use_container_width=True, hide_index=True, height=600)
        with col2:
            st.markdown("#### 🏛️ NFe Autorizadas – SEFAZ")
            if df_disc_sefaz.empty:
                st.info("Sem dados SEFAZ para este filtro.")
            else:
                st.dataframe(df_disc_sefaz, use_container_width=True, hide_index=True, height=600)


if tab == "Nf Saída":
    st.markdown("## 📤 Nota Fiscal de Saída")
    st.markdown("---")

    subtab1, subtab2 = st.tabs(["🔄 Comparativo & Agregado", "🔍 Discriminado"])

    # ── subtab1: Comparativo + Agregado ────────────────────────────────────
    with subtab1:
        f1, f2 = st.columns(2)
        with f1:
            tipo_nf_saida = st.selectbox(
                "Tipo de Operação",
                ["Oper. Interna", "Interestadual", "Do Exterior"],
                key="tipo_nfe_sai",
            )
        with f2:
            mes_nf_saida = st.selectbox(
                "Mês",
                ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                key="mes_nfe_sai",
            )

        # ── Carga ──────────────────────────────────────────────────────────
        df_sql_sai = get_saida(int(cod_empresa), "nfe").copy()
        df_sql_sai = df_sql_sai[df_sql_sai["tipo"] == tipo_nf_saida]
        if not df_sql_sai.empty and mes_nf_saida != "TODOS":
            df_sql_sai = df_sql_sai[df_sql_sai["mes"] == mes_nf_saida]

        TABELAS_NFE_SAI = [
            ("Autorizadas",                   "nf_saida_autorizadas",  "qtd", "valor"),
            ("Não Declaradas na EFD",         "nf_saida_nao_declaradas", "qtd", "valor"),
            ("Valor Divergente na EFD",       "nf_saida_divergentes",    "qtd", "valor"),
            ("Canceladas c/ Decl. Destinat.", "nf_saida_canceladas",     "qtd", "valor"),
        ]
        dfs_nfe_sai = {}
        for titulo, tabela, col_qtd, col_val in TABELAS_NFE_SAI:
            df_t = get_and_proccess_table(tabela, cnpj_empresa)
            df_t = filtrar_df(df_t, ano, tipo_nf_saida, mes_nf_saida)
            dfs_nfe_sai[titulo] = (df_t, col_qtd, col_val)

        df_aut_s   = dfs_nfe_sai["Autorizadas"][0]
        df_ndecl_s = dfs_nfe_sai["Não Declaradas na EFD"][0]
        df_divg_s  = dfs_nfe_sai["Valor Divergente na EFD"][0]
        df_canc_s  = dfs_nfe_sai["Canceladas c/ Decl. Destinat."][0]

        # ── Painel Comparativo SQL × SEFAZ ────────────────────────────────
        st.markdown("### 🔄 Comparação SQL Central × SEFAZ (Autorizadas)")
        st.caption(
            "Compara as NFe registradas como saída no SQL Central contra as NFe "
            "autorizadas pela SEFAZ, agrupadas por mês."
        )
        _painel_comparativo(
            df_sql=df_sql_sai,
            df_sefaz=df_aut_s,
            col_val_sql="valor",
            col_qtd_sefaz="qtd",
            col_val_sefaz="valor",
            prefix="nfe_sai",
        )

        st.markdown("---")

        # ── Indicadores de Risco ──────────────────────────────────────────
        st.markdown("### ⚠️ Indicadores de Risco")
        ir1, ir2, ir3, ir4 = st.columns(4)
        ir1.metric(
            "🟥 Não Declaradas – Qtd", int(_safe_sum(df_ndecl_s, "qtd")),
            help="NFe autorizadas que não foram declaradas na EFD.",
        )
        ir2.metric("🟥 Não Declaradas – Valor", _fmt_brl(_safe_sum(df_ndecl_s, "valor")))
        ir3.metric(
            "🟡 Valor Divergente – Qtd", int(_safe_sum(df_divg_s, "qtd")),
            help="NFe saída declaradas com valor diferente na EFD.",
        )
        ir4.metric(
            "🟠 Canceladas c/ Decl. – Qtd", int(_safe_sum(df_canc_s, "qtd")),
            help="NFe canceladas que ainda aparecem declaradas na EFD do destinatário.",
        )

        st.markdown("---")

        # ── Gráficos de detalhe ───────────────────────────────────────────
        st.markdown("### 📊 Detalhe por Categoria")
        gc1, gc2 = st.columns(2)
        with gc1:
            _bar_chart_mensal(df_ndecl_s, "valor", "Não Declaradas – Valor Mensal",       cor="#F76C6C", key="nfe_sai_ndecl_val")
        with gc2:
            _bar_chart_mensal(df_divg_s,  "valor", "Valor Divergente – Valor Mensal",     cor="#F7B731", key="nfe_sai_divg_val")

        gc3, gc4 = st.columns(2)
        with gc3:
            _bar_chart_mensal(df_ndecl_s, "qtd",   "Não Declaradas – Qtd Mensal",         cor="#FC5C65", key="nfe_sai_ndecl_qtd")
        with gc4:
            _bar_chart_mensal(df_canc_s,  "qtd",   "Canceladas c/ Decl. – Qtd Mensal",    cor="#8854D0", key="nfe_sai_canc_qtd")

        st.markdown("---")

        # ── Dados Brutos ──────────────────────────────────────────────────
        st.markdown("### 🗂️ Dados Brutos")
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown("#### 🏢 NFe SQL Central (ERP)")
            if df_sql_sai.empty:
                st.info("Nenhuma NFe encontrada no SQL Central para o filtro selecionado.")
            else:
                st.dataframe(df_sql_sai, use_container_width=True, hide_index=True, height=450)
        with col2:
            for titulo, (df_t, _, _) in dfs_nfe_sai.items():
                st.markdown(f"#### 📋 {titulo}")
                if df_t.empty:
                    st.info("Sem dados.")
                else:
                    st.dataframe(df_t, use_container_width=True, hide_index=True)
                st.markdown("")

    # ── subtab2: Discriminado ──────────────────────────────────────────────
    with subtab2:
        st.markdown("### 🔍 NFe Discriminadas (nota a nota)")
        mes_nf_sai_disc = st.selectbox(
            "Mês",
            ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            key="mes_nfe_sai_disc",
        )

        # SQL Central
        df_sql_sai_disc = get_saida(int(cod_empresa), "nfe").copy()
        if not df_sql_sai_disc.empty and mes_nf_sai_disc != "TODOS":
            df_sql_sai_disc = df_sql_sai_disc[df_sql_sai_disc["mes"] == mes_nf_sai_disc]

        # SEFAZ discriminado
        df_disc_sai_sefaz = get_and_proccess_table("nf_saida", cnpj_empresa)
        if not df_disc_sai_sefaz.empty and "emissao" in df_disc_sai_sefaz.columns:
            df_disc_sai_sefaz["ano"] = pd.to_datetime(df_disc_sai_sefaz["emissao"], errors="coerce").dt.year
            df_disc_sai_sefaz["mes"] = pd.to_datetime(df_disc_sai_sefaz["emissao"], errors="coerce").dt.month
            df_disc_sai_sefaz["dia"] = pd.to_datetime(df_disc_sai_sefaz["emissao"], errors="coerce").dt.day
        else:
            for _c in ["ano", "mes", "dia"]:
                df_disc_sai_sefaz[_c] = None

        if mes_nf_sai_disc != "TODOS" and not df_disc_sai_sefaz.empty and "mes" in df_disc_sai_sefaz.columns:
            df_disc_sai_sefaz = df_disc_sai_sefaz[
                pd.to_numeric(df_disc_sai_sefaz["mes"], errors="coerce") == mes_nf_sai_disc
            ]

        # Métricas rápidas
        _metric_row([
            ("SQL Central – Qtd",   _safe_len(df_sql_sai_disc)),
            ("SQL Central – Valor", _fmt_brl(_safe_sum(df_sql_sai_disc, "valor"))),
            ("SEFAZ – Qtd",         _safe_len(df_disc_sai_sefaz)),
            ("SEFAZ – Valor",       _fmt_brl(_safe_sum(df_disc_sai_sefaz, "valor"))),
        ])
        st.markdown("")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🏢 NFe SQL Central (ERP)")
            if df_sql_sai_disc.empty:
                st.info("Sem dados no SQL Central para este filtro.")
            else:
                st.dataframe(df_sql_sai_disc, use_container_width=True, hide_index=True, height=600)
        with col2:
            st.markdown("#### 🏛️ NFe Autorizadas – SEFAZ")
            if df_disc_sai_sefaz.empty:
                st.info("Sem dados SEFAZ para este filtro.")
            else:
                st.dataframe(df_disc_sai_sefaz, use_container_width=True, hide_index=True, height=600)

if tab == "NFCe e CFe":
    st.markdown("## 🧾 NFC-e e CF-e (Venda ao Consumidor)")
    st.markdown("---")

    subtab1, subtab2 = st.tabs(["🔄 Comparativo & Agregado", "🔍 Discriminado"])

    # ── subtab1: Comparativo + Agregado ────────────────────────────────────
    with subtab1:
        mes_aconsumidor = st.selectbox(
            "Mês",
            ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            key="mes_nfce_agr",
        )

        # ── Carga SQL Central (CFe + NFCe) ─────────────────────────────────
        df_cfe_sql  = get_CFe(int(cod_empresa)).copy()
        df_nfce_sql = get_saida(int(cod_empresa), "nfce").copy()

        if not df_cfe_sql.empty and mes_aconsumidor != "TODOS":
            df_cfe_sql = df_cfe_sql[df_cfe_sql["mes"] == mes_aconsumidor]
        if not df_nfce_sql.empty and mes_aconsumidor != "TODOS":
            df_nfce_sql = df_nfce_sql[df_nfce_sql["mes"] == mes_aconsumidor]

        # ── Carga SEFAZ ────────────────────────────────────────────────────
        TABELAS_NFCE = [
            ("CF-e Autorizados",           "cfe_autorizadas",       "qtd", "valor"),
            ("NFC-e Autorizados",          "nfce_autorizadas",      "qtd", "valor"),
            ("Divergência de Valores EFD", "nfce_cfe_divergencias", None,  "valor"),
            ("Cancelados",                 "nfce_cfe_cancelados",   "qtd", "valor"),
            ("Emitidos com Ressalva",      "nfce_cfe_ressalva",     "qtd", "valor"),
        ]
        dfs_nfce = {}
        for titulo, tabela, col_qtd, col_val in TABELAS_NFCE:
            df_t = get_and_proccess_table(tabela, cnpj_empresa)
            df_t = filtrar_df(df_t, ano, "TODAS", mes_aconsumidor)
            dfs_nfce[titulo] = (df_t, col_qtd, col_val)

        df_cfe_aut  = dfs_nfce["CF-e Autorizados"][0]
        df_nfce_aut = dfs_nfce["NFC-e Autorizados"][0]
        df_divg     = dfs_nfce["Divergência de Valores EFD"][0]
        df_canc     = dfs_nfce["Cancelados"][0]
        df_ress     = dfs_nfce["Emitidos com Ressalva"][0]

        # ── Métricas de resumo ─────────────────────────────────────────────
        st.markdown("### 📊 Resumo")
        rm1, rm2, rm3, rm4, rm5, rm6 = st.columns(6)
        rm1.metric("🏪 CFe SQL – Qtd",    _safe_len(df_cfe_sql))
        rm2.metric("🏪 CFe SQL – Valor",  _fmt_brl(_safe_sum(df_cfe_sql, "valor")))
        rm3.metric("📱 NFCe SQL – Qtd",   _safe_len(df_nfce_sql))
        rm4.metric("📱 NFCe SQL – Valor", _fmt_brl(_safe_sum(df_nfce_sql, "valor")))
        rm5.metric("🏛️ CFe SEFAZ – Qtd",  int(_safe_sum(df_cfe_aut,  "qtd")))
        rm6.metric("🏛️ NFCe SEFAZ – Qtd", int(_safe_sum(df_nfce_aut, "qtd")))

        st.markdown("---")

        # ── Painel Comparativo CFe: SQL × SEFAZ ───────────────────────────
        st.markdown("### 🔄 Comparação CFe: SQL Central × SEFAZ")
        st.caption("CF-e emitidos no SQL Central vs. CF-e autorizados na SEFAZ, por mês.")
        _painel_comparativo(
            df_sql=df_cfe_sql,
            df_sefaz=df_cfe_aut,
            col_val_sql="valor",
            col_qtd_sefaz="qtd",
            col_val_sefaz="valor",
            prefix="cfe",
        )

        st.markdown("---")

        # ── Painel Comparativo NFCe: SQL × SEFAZ ──────────────────────────
        st.markdown("### 🔄 Comparação NFC-e: SQL Central × SEFAZ")
        st.caption("NFC-e emitidas no SQL Central vs. NFC-e autorizadas na SEFAZ, por mês.")
        _painel_comparativo(
            df_sql=df_nfce_sql,
            df_sefaz=df_nfce_aut,
            col_val_sql="valor",
            col_qtd_sefaz="qtd",
            col_val_sefaz="valor",
            prefix="nfce",
        )

        st.markdown("---")

        # ── Indicadores de Risco ──────────────────────────────────────────
        st.markdown("### ⚠️ Indicadores de Risco")
        ir1, ir2, ir3, ir4 = st.columns(4)
        ir1.metric("🟥 Divergência EFD – Valor", _fmt_brl(_safe_sum(df_divg, "valor")),
                   help="Diferença de valores declarados na EFD entre CFe/NFCe.")
        ir2.metric("🟥 Cancelados – Qtd",        int(_safe_sum(df_canc, "qtd")))
        ir3.metric("🟥 Cancelados – Valor",      _fmt_brl(_safe_sum(df_canc, "valor")))
        ir4.metric("🟡 Com Ressalva – Qtd",      int(_safe_sum(df_ress, "qtd")),
                   help="Documentos emitidos com ressalva fiscal.")

        st.markdown("---")

        # ── Gráficos de detalhe ───────────────────────────────────────────
        st.markdown("### 📊 Detalhe por Categoria")
        gc1, gc2 = st.columns(2)
        with gc1:
            _bar_chart_mensal(df_canc,  "valor", "Cancelados – Valor Mensal",      cor="#F76C6C", key="nfce_canc_val")
        with gc2:
            _bar_chart_mensal(df_ress,  "qtd",   "Com Ressalva – Qtd Mensal",      cor="#F7B731", key="nfce_ress_qtd")

        gc3, gc4 = st.columns(2)
        with gc3:
            _bar_chart_mensal(df_cfe_aut,  "valor", "CFe Autorizados – Valor Mensal",  cor="#4F8EF7", key="cfe_aut_val")
        with gc4:
            _bar_chart_mensal(df_nfce_aut, "valor", "NFCe Autorizados – Valor Mensal", cor="#43C59E", key="nfce_aut_val")

        st.markdown("---")

        # ── Dados Brutos ──────────────────────────────────────────────────
        st.markdown("### 🗂️ Dados Brutos SEFAZ")
        for titulo, (df_t, _, _) in dfs_nfce.items():
            with st.expander(f"📋 {titulo}", expanded=False):
                if df_t.empty:
                    st.info("Sem dados.")
                else:
                    st.dataframe(df_t, use_container_width=True, hide_index=True)

    # ── subtab2: Discriminado ──────────────────────────────────────────────
    with subtab2:
        st.markdown("### 🔍 CFe e NFC-e Discriminados (documento a documento)")
        mes_dconsumidor = st.selectbox(
            "Mês",
            ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            key="mes_nfce_disc",
        )

        # SQL Central
        df_cfe_disc  = get_CFe(int(cod_empresa)).copy()
        df_nfce_disc = get_saida(int(cod_empresa), "nfce").copy()
        if mes_dconsumidor != "TODOS":
            if not df_cfe_disc.empty:
                df_cfe_disc = df_cfe_disc[df_cfe_disc["mes"] == mes_dconsumidor]
            if not df_nfce_disc.empty:
                df_nfce_disc = df_nfce_disc[df_nfce_disc["mes"] == mes_dconsumidor]

        # SEFAZ discriminado
        df_disc_sefaz = get_and_proccess_table("nfce_cfe_discriminado", cnpj_empresa)
        if not df_disc_sefaz.empty and "emissao" in df_disc_sefaz.columns:
            df_disc_sefaz["ano"] = pd.to_datetime(df_disc_sefaz["emissao"], errors="coerce").dt.year
            df_disc_sefaz["mes"] = pd.to_datetime(df_disc_sefaz["emissao"], errors="coerce").dt.month
            df_disc_sefaz["dia"] = pd.to_datetime(df_disc_sefaz["emissao"], errors="coerce").dt.day
        else:
            for _c in ["ano", "mes", "dia"]:
                df_disc_sefaz[_c] = None

        if mes_dconsumidor != "TODOS" and not df_disc_sefaz.empty and "mes" in df_disc_sefaz.columns:
            df_disc_sefaz = df_disc_sefaz[
                pd.to_numeric(df_disc_sefaz["mes"], errors="coerce") == mes_dconsumidor
            ]

        # Métricas rápidas
        _metric_row([
            ("CFe SQL – Qtd",    _safe_len(df_cfe_disc)),
            ("CFe SQL – Valor",  _fmt_brl(_safe_sum(df_cfe_disc,  "valor"))),
            ("NFCe SQL – Qtd",   _safe_len(df_nfce_disc)),
            ("NFCe SQL – Valor", _fmt_brl(_safe_sum(df_nfce_disc, "valor"))),
            ("SEFAZ – Qtd",      _safe_len(df_disc_sefaz)),
            ("SEFAZ – Valor",    _fmt_brl(_safe_sum(df_disc_sefaz, "valor"))),
        ])
        st.markdown("")

        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.markdown("#### 🏪 CFe SQL Central")
            if df_cfe_disc.empty:
                st.info("Sem dados.")
            else:
                st.dataframe(df_cfe_disc, use_container_width=True, hide_index=True, height=500)
        with dc2:
            st.markdown("#### 📱 NFC-e SQL Central")
            if df_nfce_disc.empty:
                st.info("Sem dados.")
            else:
                st.dataframe(df_nfce_disc, use_container_width=True, hide_index=True, height=500)
        with dc3:
            st.markdown("#### 🏛️ CFe/NFCe – SEFAZ")
            if df_disc_sefaz.empty:
                st.info("Sem dados.")
            else:
                st.dataframe(df_disc_sefaz, use_container_width=True, hide_index=True, height=500)


if tab == "Pendências Fiscais":
    st.markdown("## 🔔 Pendências Fiscais")
    st.markdown("---")

    df_pend = get_and_proccess_table("pendencias_fiscais", cnpj_empresa)

    # Garante colunas
    for _col in ["indicador", "descricao", "atualizacao", "qtd", "valor"]:
        if _col not in df_pend.columns:
            df_pend[_col] = None

    df_pend["valor"] = pd.to_numeric(df_pend["valor"], errors="coerce").fillna(0)
    df_pend["qtd"]   = pd.to_numeric(df_pend["qtd"],   errors="coerce").fillna(0)

    if df_pend.empty:
        st.info("Nenhuma pendência fiscal encontrada para este contribuinte.")
    else:
        # ── Métricas ───────────────────────────────────────────────────────
        st.markdown("### 📊 Resumo")
        pm1, pm2, pm3 = st.columns(3)
        pm1.metric("📋 Total de Pendências",  len(df_pend))
        pm2.metric("💰 Valor Total",          _fmt_brl(df_pend["valor"].sum()))
        pm3.metric("🔢 Qtd Total de Itens",   int(df_pend["qtd"].sum()))

        st.markdown("---")

        # ── Gráfico por indicador (valor) ──────────────────────────────────
        if "indicador" in df_pend.columns and df_pend["indicador"].notna().any():
            df_graf_pend = (
                df_pend.groupby("indicador", as_index=False)
                .agg(valor_total=("valor", "sum"), qtd_total=("qtd", "sum"))
                .sort_values("valor_total", ascending=True)
            )

            pg1, pg2 = st.columns(2)
            with pg1:
                fig_pend_val = px.bar(
                    df_graf_pend, x="valor_total", y="indicador",
                    orientation="h",
                    title="Valor por Indicador de Pendência",
                    color="valor_total",
                    color_continuous_scale=["#4F8EF7", "#F76C6C"],
                    text="valor_total",
                )
                fig_pend_val.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#FAFAFA", title_font_size=14,
                    margin=dict(l=10, r=10, t=45, b=10),
                    coloraxis_showscale=False,
                    yaxis=dict(showgrid=False),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                )
                fig_pend_val.update_traces(
                    texttemplate="%{x:,.0f}", textposition="outside", textfont_size=10
                )
                st.plotly_chart(fig_pend_val, use_container_width=True, key="pend_val_ind")

            with pg2:
                fig_pend_qtd = px.bar(
                    df_graf_pend, x="qtd_total", y="indicador",
                    orientation="h",
                    title="Quantidade por Indicador de Pendência",
                    color="qtd_total",
                    color_continuous_scale=["#43C59E", "#F7B731"],
                    text="qtd_total",
                )
                fig_pend_qtd.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#FAFAFA", title_font_size=14,
                    margin=dict(l=10, r=10, t=45, b=10),
                    coloraxis_showscale=False,
                    yaxis=dict(showgrid=False),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                )
                fig_pend_qtd.update_traces(
                    texttemplate="%{x:.0f}", textposition="outside", textfont_size=10
                )
                st.plotly_chart(fig_pend_qtd, use_container_width=True, key="pend_qtd_ind")

        st.markdown("---")

        # ── Tabela estilizada ──────────────────────────────────────────────
        st.markdown("### 🗂️ Detalhamento")

        # Destaque de linhas por valor: vermelho se valor > 0
        def _style_pend_row(row):
            try:
                v = float(row["valor"]) if row["valor"] is not None else 0
                cor = "rgba(247,108,108,0.18)" if v > 0 else ""
                return [f"background-color: {cor}" for _ in row]
            except Exception:
                return ["" for _ in row]

        styled_pend = (
            df_pend.style
            .apply(_style_pend_row, axis=1)
            .format({"valor": "{:,.2f}", "qtd": "{:.0f}"})
        )
        st.dataframe(styled_pend, use_container_width=True, hide_index=True)


if tab == "Métodos de Pagamento":
    st.markdown("## 💳 Métodos de Pagamento")
    st.markdown("---")

    mes_pagamento = st.selectbox(
        "Mês",
        ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        key="mes_pagamento",
    )

    df_pag = get_and_proccess_table("metodo_pagamento", cnpj_empresa)

    # Garante colunas
    for _col in ["entidade", "mes", "ano", "valor"]:
        if _col not in df_pag.columns:
            df_pag[_col] = None

    df_pag["valor"] = pd.to_numeric(df_pag["valor"], errors="coerce").fillna(0)
    df_pag["mes"]   = pd.to_numeric(df_pag["mes"],   errors="coerce")

    if mes_pagamento != "TODOS":
        df_pag = df_pag[df_pag["mes"] == mes_pagamento]

    if df_pag.empty:
        st.info("Nenhum dado de método de pagamento encontrado para este filtro.")
    else:
        # ── Métricas ───────────────────────────────────────────────────────
        st.markdown("### 📊 Resumo")
        pmc1, pmc2, pmc3 = st.columns(3)
        pmc1.metric("💰 Valor Total",       _fmt_brl(df_pag["valor"].sum()))
        pmc2.metric("🏦 Entidades únicas",  df_pag["entidade"].nunique() if "entidade" in df_pag.columns else "–")
        pmc3.metric("📋 Registros",         len(df_pag))

        st.markdown("---")

        gc1, gc2 = st.columns(2)

        # ── Gráfico de pizza por entidade ──────────────────────────────────
        with gc1:
            if "entidade" in df_pag.columns and df_pag["entidade"].notna().any():
                df_ent = (
                    df_pag.groupby("entidade", as_index=False)["valor"]
                    .sum()
                    .sort_values("valor", ascending=False)
                )
                fig_pie = px.pie(
                    df_ent, names="entidade", values="valor",
                    title="Distribuição por Entidade/Método",
                    color_discrete_sequence=CTE_PALETTE,
                    hole=0.4,
                )
                fig_pie.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#FAFAFA", title_font_size=14,
                    margin=dict(l=10, r=10, t=45, b=10),
                    legend=dict(orientation="v", x=1, y=0.5),
                )
                fig_pie.update_traces(textinfo="percent+label", textfont_size=11)
                st.plotly_chart(fig_pie, use_container_width=True, key="pag_pie_entidade")
            else:
                st.info("Sem coluna 'entidade' para gráfico de distribuição.")

        # ── Gráfico de barras por mês ───────────────────────────────────────
        with gc2:
            if mes_pagamento == "TODOS" and "mes" in df_pag.columns and df_pag["mes"].notna().any():
                df_pag_mes = (
                    df_pag.dropna(subset=["mes"])
                    .groupby("mes", as_index=False)["valor"]
                    .sum()
                    .sort_values("mes")
                )
                df_pag_mes["mes_nome"] = df_pag_mes["mes"].map(MESES_NOME).fillna(df_pag_mes["mes"].astype(str))
                ordem_pag = [v for v in MESES_NOME.values() if v in df_pag_mes["mes_nome"].values]
                df_pag_mes["mes_nome"] = pd.Categorical(df_pag_mes["mes_nome"], categories=ordem_pag, ordered=True)
                df_pag_mes = df_pag_mes.sort_values("mes_nome")

                fig_pag_mes = px.bar(
                    df_pag_mes, x="mes_nome", y="valor",
                    title="Valor Total por Mês",
                    color_discrete_sequence=["#4F8EF7"],
                    text_auto=True,
                )
                fig_pag_mes.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#FAFAFA", title_font_size=14,
                    margin=dict(l=10, r=10, t=45, b=10),
                    xaxis=dict(showgrid=False, title="Mês"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                )
                fig_pag_mes.update_traces(marker_line_width=0, textfont_size=10)
                st.plotly_chart(fig_pag_mes, use_container_width=True, key="pag_bar_mes")
            else:
                # Mês específico: barras por entidade
                if "entidade" in df_pag.columns and df_pag["entidade"].notna().any():
                    df_ent2 = (
                        df_pag.groupby("entidade", as_index=False)["valor"]
                        .sum()
                        .sort_values("valor", ascending=False)
                    )
                    fig_ent_bar = px.bar(
                        df_ent2, x="entidade", y="valor",
                        title=f"Valor por Entidade – Mês {mes_pagamento}",
                        color_discrete_sequence=["#43C59E"],
                        text_auto=True,
                    )
                    fig_ent_bar.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#FAFAFA", title_font_size=14,
                        margin=dict(l=10, r=10, t=45, b=10),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                    )
                    fig_ent_bar.update_traces(marker_line_width=0, textfont_size=10)
                    st.plotly_chart(fig_ent_bar, use_container_width=True, key="pag_bar_ent")
                else:
                    st.info("Selecione 'TODOS' os meses para ver a evolução mensal.")

        st.markdown("---")

        # ── Tabela detalhada ──────────────────────────────────────────────
        st.markdown("### 🗂️ Detalhamento")
        df_pag_exib = df_pag.copy()
        df_pag_exib["mes_nome"] = pd.to_numeric(df_pag_exib["mes"], errors="coerce").map(MESES_NOME).fillna(df_pag_exib["mes"].astype(str))
        st.dataframe(
            df_pag_exib.style.format({"valor": "{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

