import streamlit as st

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


st.set_page_config(page_title="Felipe", layout="wide", initial_sidebar_state="expanded")


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


if tab == "CTe":

    subtab1, subtab2, subtab3 = st.tabs(["Créditos Indevidos", "Emissor", "Tomador"])

    with subtab1:
        df_credito_nao_tomador = get_and_proccess_table(
            "credito_indevido_nao_tomador", cnpj_empresa
        )
        df_credito_repetido = get_and_proccess_table(
            "credito_indevido_repetido", cnpj_empresa
        )

        df_credito_nao_tomador = df_credito_nao_tomador[
            df_credito_nao_tomador["ano"] == ano
        ]
        df_credito_repetido = df_credito_repetido[df_credito_repetido["ano"] == ano]

        st.subheader(
            "CTe declarados na EFD onde o contribuinte não é o tomador de serviço"
        )
        st.dataframe(df_credito_nao_tomador, width="stretch", hide_index=True)

        st.subheader(" CTe declarados repetidamente na EFD")
        st.dataframe(df_credito_repetido, width="stretch", hide_index=True)

    with subtab2:
        tipo_emissor = st.selectbox(
            "tipo_emissor", ["Oper. Interna", "Interestadual", "Do Exterior"]
        )
        mes_emissor = st.selectbox(
            "mes_emissor", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_saida(int(cod_empresa), "cte")
            df = df[df["tipo"] == tipo_emissor]
            if mes_emissor != "TODOS":
                df = df[df["mes"] == mes_emissor]

            st.subheader("CTe SQL Central")
            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:
            TABELAS_CTE = [
                ("Emitidos", "cte_emissor_saida_emitidos"),
                (
                    "Não Declarados ou Valor Divergente",
                    "cte_emissor_saida_nao_declarados_ou_valor_divergente",
                ),
                ("CTe emitidos em contingência", "cte_emissor_saida_contingencia"),
                ("CTe cancelados", "cte_emissor_saida_cancelados"),
            ]

            for titulo, tabela in TABELAS_CTE:
                df = get_and_proccess_table(tabela, cnpj_empresa)
                df = filtrar_df(df, ano, tipo_emissor, mes_emissor)

                st.subheader(titulo)
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                )

    with subtab3:
        tipo_tomador = st.selectbox(
            "tipo_tomador", ["Oper. Interna", "Interestadual", "Do Exterior"]
        )
        mes_tomador = st.selectbox(
            "mes_tomador", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )
        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_entrada(int(cod_empresa), "cte")

            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:

            TABELAS_CTE = [
                (
                    "CTe destinados ao contribuinte tomador do serviço",
                    "cte_tomador_destinados_contribuinte",
                ),
                (
                    "CTe não declarados ou declarados com valor diferente na EFD",
                    "cte_tomador_nao_declaradas_ou_divergente",
                ),
                (
                    "CTe com NFe não registradas no SITRAM",
                    "cte_tomador_nao_registradas_sitram",
                ),
                ("CTe cancelados", "cte_emissor_saida_cancelados"),
            ]

            for titulo, tabela in TABELAS_CTE:
                df = get_and_proccess_table(tabela, cnpj_empresa)
                df = filtrar_df(df, ano, tipo_tomador, mes_tomador)

                st.subheader(titulo)
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                )


if tab == "Débitos Fiscais":
    df_debitos_fiscais = get_and_proccess_table("debitos_fiscais", cnpj_empresa)
    df_debitos_fiscais = df_debitos_fiscais[
        ["vencimento", "codigo", "descricao", "vencido", "referencia", "valor"]
    ]

    st.subheader("Débitos Fiscais")
    st.dataframe(
        df_debitos_fiscais,
        width="stretch",
        hide_index=True,
    )

if tab == "Nf Entrada":
    subtab1, subtab2 = st.tabs(["Agregado", "Discriminado"])

    with subtab1:
        tipo_nf_entrada = st.selectbox(
            "tipo_nf_entrada", ["Oper. Interna", "Interestadual", "Do Exterior"]
        )
        mes_nf_entrada = st.selectbox(
            "mes_nf_entrada", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_entrada(int(cod_empresa), "nfe")

            st.subheader("Nfe SQL Central")
            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            if mes_nf_entrada != "TODOS":
                df = df[df["mes"] == mes_nf_entrada]

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:
            TABELAS_CTE = [
                ("NFe Autorizadas para o Contribuinte", "nf_entrada_autorizadas"),
                (
                    "NFe não Declaradas na EFD",
                    "nf_entrada_nao_declaradas",
                ),
                ("NFe Declaradas com Valor Diferente na EFD", "nf_entrada_divergentes"),
                ("NFe não Registradas no SITRAM", "nf_entrada_nao_registradas_sitram"),
            ]

            for titulo, tabela in TABELAS_CTE:
                df = get_and_proccess_table(tabela, cnpj_empresa)
                df = filtrar_df(df, ano, tipo_nf_entrada, mes_nf_entrada)

                st.subheader(titulo)
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                )

    with subtab2:
        mes_nf_entrada_discriminado = st.selectbox(
            "mes_dentrada", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_entrada(int(cod_empresa), "nfe")

            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            if mes_nf_entrada_discriminado != "TODOS":
                df = df[df["mes"] == mes_nf_entrada_discriminado]

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:
            df_nf_entrada_discriminado = get_and_proccess_table(
                "nf_entrada_discriminado", cnpj_empresa
            )

            if len(df_nf_entrada_discriminado) > 0:
                df_nf_entrada_discriminado["ano"] = df_nf_entrada_discriminado[
                    "emissao"
                ].dt.year
                df_nf_entrada_discriminado["mes"] = df_nf_entrada_discriminado[
                    "emissao"
                ].dt.month
                df_nf_entrada_discriminado["dia"] = df_nf_entrada_discriminado[
                    "emissao"
                ].dt.day

            else:
                df_nf_entrada_discriminado["ano"] = ""
                df_nf_entrada_discriminado["mes"] = ""
                df_nf_entrada_discriminado["dia"] = ""

            if mes_nf_entrada_discriminado != "TODOS":
                df_nf_entrada_discriminado = df_nf_entrada_discriminado[
                    df_nf_entrada_discriminado["mes"] == mes_nf_entrada_discriminado
                ]

            st.subheader("NFe Autorizadas para o Contribuinte")
            st.dataframe(
                df_nf_entrada_discriminado,
                width="stretch",
                hide_index=True,
            )

if tab == "Nf Saída":
    subtab1, subtab2 = st.tabs(["Agregado", "Discriminado"])

    with subtab1:
        tipo_nf_saida = st.selectbox(
            "tipo_nf_saida", ["Oper. Interna", "Interestadual", "Do Exterior"]
        )

        mes_nf_saida = st.selectbox(
            "mes_nf_saida", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_saida(int(cod_empresa), "nfe")

            if mes_nf_saida != "TODOS":
                df = df[df["mes"] == mes_nf_saida]

            st.subheader("Nfe SQL Central")

            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:

            TABELAS_CTE = [
                ("NFe Autorizadas", "nf_saida_autorizadas"),
                (
                    "NFe não Declaradas na EFD",
                    "nf_saida_nao_declaradas",
                ),
                ("NFe Declaradas com Valor Diferente na EFD", "nf_saida_divergentes"),
                (
                    "NFe Canceladas e Declaradas na EFD do Destinatário",
                    "nf_saida_canceladas",
                ),
            ]

            for titulo, tabela in TABELAS_CTE:
                df = get_and_proccess_table(tabela, cnpj_empresa)
                df = filtrar_df(df, ano, tipo_nf_saida, mes_nf_saida)

                st.subheader(titulo)
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                )

    with subtab2:
        mes_dsaida = st.selectbox(
            "mes_dsaida", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )
        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_saida(int(cod_empresa), "nfe")
            if mes_dsaida != "TODOS":
                df = df[df["mes"] == mes_dsaida]

            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:
            df_nf_saida = get_and_proccess_table("nf_saida", cnpj_empresa)

            if len(df_nf_saida) > 0:
                df_nf_saida["ano"] = df_nf_saida["emissao"].dt.year
                df_nf_saida["mes"] = df_nf_saida["emissao"].dt.month
                df_nf_saida["dia"] = df_nf_saida["emissao"].dt.day

            else:
                df_nf_saida["ano"] = ""
                df_nf_saida["mes"] = ""
                df_nf_saida["dia"] = ""

            if mes_dsaida != "TODOS":
                df_nf_saida = df_nf_saida[df_nf_saida["mes"] == df_nf_saida]

            st.subheader("NFe Autorizadas")
            st.dataframe(
                df_nf_saida,
                width="stretch",
                hide_index=True,
            )

if tab == "NFCe e CFe":
    subtab1, subtab2 = st.tabs(["Agregado", "Discriminado"])

    with subtab1:
        mes_aconsumidor = st.selectbox(
            "mes_acfe", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            df = get_CFe(int(cod_empresa))

            st.subheader("Nfe SQL Central")
            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            if mes_aconsumidor != "TODOS":
                df = df[df["mes"] == mes_aconsumidor]

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:

            TABELAS_CTE = [
                ("CF-e Autorizados", "cfe_autorizadas"),
                (
                    "NFC-e Autorizados",
                    "nfce_autorizadas",
                ),
                ("Divergência de Valores na EFD", "nfce_cfe_divergencias"),
                ("Cancelados", "nfce_cfe_cancelados"),
                ("Emitidos com ressalva", "nfce_cfe_ressalva"),
            ]

            for titulo, tabela in TABELAS_CTE:
                df = get_and_proccess_table(tabela, cnpj_empresa)
                df = filtrar_df(df, ano, "TODAS", mes_aconsumidor)

                st.subheader(titulo)
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                )

    with subtab2:
        mes_dconsumidor = st.selectbox(
            "mes_dconsumidor", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )

        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.subheader("CFe")
            df = get_CFe(int(cod_empresa))
            if mes_dconsumidor != "TODOS":
                df = df[df["mes"] == mes_dconsumidor]

            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

            st.subheader("NFCe")
            df_nfce = get_saida(int(cod_empresa), "nfce")
            if mes_dconsumidor != "TODOS":
                df = df[df["mes"] == mes_dconsumidor]

            st.write(f"Quantidade: {len(df)} - Valor: R$ {df['valor'].sum()}")

            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                height=800,
            )

        with col2:
            df_nfce_cfe_discriminado = get_and_proccess_table(
                "nfce_cfe_discriminado", cnpj_empresa
            )

            if len(df_nfce_cfe_discriminado) > 0:
                df_nfce_cfe_discriminado["ano"] = df_nfce_cfe_discriminado[
                    "emissao"
                ].dt.year
                df_nfce_cfe_discriminado["mes"] = df_nfce_cfe_discriminado[
                    "emissao"
                ].dt.month
                df_nfce_cfe_discriminado["dia"] = df_nfce_cfe_discriminado[
                    "emissao"
                ].dt.day

            else:
                df_nfce_cfe_discriminado["ano"] = ""
                df_nfce_cfe_discriminado["mes"] = ""
                df_nfce_cfe_discriminado["dia"] = ""

            if mes_dconsumidor != "TODOS":
                df_nfce_cfe_discriminado = df_nfce_cfe_discriminado[
                    df_nfce_cfe_discriminado["mes"] == mes_dconsumidor
                ]

            st.subheader("Cfe e NFCe")
            st.dataframe(
                df_nfce_cfe_discriminado,
                width="stretch",
                hide_index=True,
            )

if tab == "Pendências Fiscais":

    df_pendencias_fiscais = get_and_proccess_table("pendencias_fiscais", cnpj_empresa)

    st.subheader("Pendências Fiscais")
    st.dataframe(
        df_pendencias_fiscais,
        width="stretch",
        hide_index=True,
    )

if tab == "Métodos de Pagamento":
    mes_pagamento = st.selectbox(
        "mes_pagamento", ["TODOS", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    )
    df_pendencias_fiscais = get_and_proccess_table("metodo_pagamento", cnpj_empresa)
    if mes_pagamento != "TODOS":
        df_pendencias_fiscais = df_pendencias_fiscais[
            df_pendencias_fiscais["mes"] == mes_pagamento
        ]

    st.subheader("metodo_pagamento")
    st.dataframe(
        df_pendencias_fiscais,
        width="stretch",
        hide_index=True,
    )
