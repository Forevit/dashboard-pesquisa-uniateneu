import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Satisfação — UniAteneu",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #e2e8f0;
    }
    div[data-testid="metric-container"] label {
        font-size: 13px !important;
        color: #64748b !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES DO PROJETO
# ─────────────────────────────────────────────────────────────
CSV_PATH = "baseTratada.csv"

PERGUNTAS = [
    "Participação (calendário)",
    "Participação (fóruns/chat)",
    "Uso do material didático",
    "Comunicação e interação",
    "Qualidade E-book",
    "Qualidade Scorm",
    "Qualidade Videoaula",
    "Clareza do material",
    "Conformidade atividades/material",
    "Organização do AVA",
    "Didática do professor",
    "Atendimento da tutoria",
    "Cronograma da tutoria",
    "Clareza feedback tutor",
    "Domínio do tutor",
    "Esclarecimento de dúvidas",
    "Atendimento presencial",
]

ORDEM_ESCALA = [
    "Muito satisfeito",
    "Satisfeito",
    "Parcialmente satisfeito",
    "Insatisfeito",
    "Muito insatisfeito",
    "Não sei avaliar",
]

CORES = {
    "Muito satisfeito": "#1D9E75",
    "Satisfeito": "#378ADD",
    "Parcialmente satisfeito": "#EF9F27",
    "Insatisfeito": "#D85A30",
    "Muito insatisfeito": "#A32D2D",
    "Não sei avaliar": "#888780",
}

COLUNAS_OBRIGATORIAS = {
    "SEMESTRE", "NOME", "RA", "DISCIPLINA", "ITEM_TIPO", "VALOR_ID",
    "VALOR_SELECIONADO", "PESQUISA_COMPLETADO_ID", "PESQUISA_COMPLETADO_DATA_MODIFICACAO"
}

# ─────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────
def br_int(valor: int) -> str:
    return f"{int(valor):,}".replace(",", ".")


def pct_bool(serie: pd.Series) -> float:
    if serie.empty:
        return 0.0
    return float(serie.mean() * 100)


@st.cache_data(show_spinner="Carregando e tratando a base...")
def carregar_dados(path: str):
    df_raw = pd.read_csv(path, sep=";")
    df_raw.columns = [c.strip().upper() for c in df_raw.columns]

    faltantes = COLUNAS_OBRIGATORIAS - set(df_raw.columns)
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes no CSV: {', '.join(sorted(faltantes))}")

    for col in ["ITEM_TIPO", "VALOR_SELECIONADO", "SEMESTRE", "DISCIPLINA", "NOME"]:
        df_raw[col] = df_raw[col].astype(str).str.strip()

    total_bruto = len(df_raw)

    # Remove linhas 100% duplicadas. No seu CSV, grande parte das 110k linhas são repetições idênticas.
    df_sem_duplicadas = df_raw.drop_duplicates().copy()
    duplicadas_removidas = total_bruto - len(df_sem_duplicadas)

    # Mantém respostas de múltipla escolha.
    mc = df_sem_duplicadas[df_sem_duplicadas["ITEM_TIPO"].str.lower() == "multichoice"].copy()
    total_multichoice = len(mc)

    # Segurança extra: 1 resposta por pergunta dentro de cada questionário.
    # Isso evita inflar números quando o CSV vem com duplicidade por PESQUISA_COMPLETADO_ID + VALOR_ID.
    antes_dedupe_pergunta = len(mc)
    mc = mc.drop_duplicates(subset=["PESQUISA_COMPLETADO_ID", "VALOR_ID"], keep="first").copy()
    duplicadas_pergunta = antes_dedupe_pergunta - len(mc)

    # Mapeia a pergunta pela ordem do VALOR_ID dentro do questionário.
    # É mais seguro do que usar cumcount na base bruta, porque primeiro removemos duplicidades.
    mc = mc.sort_values(["PESQUISA_COMPLETADO_ID", "VALOR_ID"])
    mc["PERGUNTA_N"] = mc.groupby("PESQUISA_COMPLETADO_ID").cumcount()

    # Mantém somente as 17 dimensões principais da pesquisa de satisfação.
    mc = mc[mc["PERGUNTA_N"].between(0, len(PERGUNTAS) - 1)].copy()
    mc["PERGUNTA"] = mc["PERGUNTA_N"].map(dict(enumerate(PERGUNTAS)))

    mc["DATA"] = pd.to_datetime(mc["PESQUISA_COMPLETADO_DATA_MODIFICACAO"], errors="coerce")
    mc["DATA_DIA"] = mc["DATA"].dt.date

    mc["SATISFEITO"] = mc["VALOR_SELECIONADO"].isin(["Muito satisfeito", "Satisfeito"])
    mc["INSATISFEITO"] = mc["VALOR_SELECIONADO"].isin(["Insatisfeito", "Muito insatisfeito"])

    diagnostico = {
        "total_bruto": total_bruto,
        "total_sem_duplicadas": len(df_sem_duplicadas),
        "duplicadas_removidas": duplicadas_removidas,
        "total_multichoice": total_multichoice,
        "duplicadas_pergunta": duplicadas_pergunta,
        "respostas_validas": len(mc),
        "questionarios": mc["PESQUISA_COMPLETADO_ID"].nunique(),
        "alunos": mc["RA"].nunique(),
    }

    return df_raw, mc, diagnostico


# ─────────────────────────────────────────────────────────────
# CARREGAMENTO
# ─────────────────────────────────────────────────────────────
try:
    df_raw, mc, diagnostico = carregar_dados(CSV_PATH)
except FileNotFoundError:
    st.error(f"❌ Arquivo **{CSV_PATH}** não encontrado. Coloque-o na mesma pasta que este script.")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro ao carregar a base: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://www.uniateneu.edu.br/wp-content/uploads/2022/07/logo-uniateneu.png",
    use_container_width=True,
)
st.sidebar.title("Filtros")

semestres = ["Todos"] + sorted(mc["SEMESTRE"].dropna().unique().tolist())
semestre_sel = st.sidebar.selectbox("Semestre", semestres)

disciplinas = ["Todas"] + sorted(mc["DISCIPLINA"].dropna().unique().tolist())
disciplina_sel = st.sidebar.selectbox("Disciplina", disciplinas)

perguntas_list = ["Todas"] + PERGUNTAS
pergunta_sel = st.sidebar.selectbox("Dimensão avaliada", perguntas_list)

# ─────────────────────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────────────────────
df = mc.copy()

if semestre_sel != "Todos":
    df = df[df["SEMESTRE"] == semestre_sel]
if disciplina_sel != "Todas":
    df = df[df["DISCIPLINA"] == disciplina_sel]
if pergunta_sel != "Todas":
    df = df[df["PERGUNTA"] == pergunta_sel]

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.title("📊 Dashboard de Satisfação de Alunos")
st.caption("Projeto de Extensão — Inovação Tecnológica Aplicada ao Mercado · UniAteneu 2025.1.1")
st.divider()

# ─────────────────────────────────────────────────────────────
# KPIs PRINCIPAIS
# ─────────────────────────────────────────────────────────────
total_alunos = df["RA"].nunique()
total_questionarios = df["PESQUISA_COMPLETADO_ID"].nunique()
total_respostas = len(df)
pct_sat = pct_bool(df["SATISFEITO"])
pct_insat = pct_bool(df["INSATISFEITO"])
nps = pct_sat - pct_insat

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("👥 Alunos únicos", br_int(total_alunos))
c2.metric("📋 Questionários", br_int(total_questionarios))
c3.metric("📝 Respostas válidas", br_int(total_respostas))
c4.metric("✅ Satisfação", f"{pct_sat:.1f}%")
c5.metric("⚠️ Insatisfação", f"{pct_insat:.1f}%")
c6.metric("⭐ NPS Educacional", f"{nps:.1f}")

# KPIs DE TRANSPARÊNCIA DA BASE
with st.expander("🔎 Diagnóstico da base de dados"):
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Registros brutos no CSV", br_int(diagnostico["total_bruto"]))
    d2.metric("Linhas duplicadas removidas", br_int(diagnostico["duplicadas_removidas"]))
    d3.metric("Registros após deduplicação", br_int(diagnostico["total_sem_duplicadas"]))
    d4.metric("Respostas válidas analisadas", br_int(diagnostico["respostas_validas"]))

    st.info(
        "A diferença entre os registros brutos e as respostas válidas acontece porque o dashboard remove "
        "linhas duplicadas e analisa somente as respostas multichoice das 17 dimensões principais da pesquisa."
    )

    qualidade = (
        mc.groupby("PESQUISA_COMPLETADO_ID")
        .size()
        .value_counts()
        .sort_index()
        .reset_index()
    )
    qualidade.columns = ["Qtd. respostas no questionário", "Qtd. questionários"]
    st.dataframe(qualidade, use_container_width=True, hide_index=True)

st.divider()

# ─────────────────────────────────────────────────────────────
# LINHA 1: DONUT + TOP DISCIPLINAS
# ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Distribuição Geral")

    dist = (
        df["VALOR_SELECIONADO"]
        .value_counts()
        .reindex(ORDEM_ESCALA)
        .fillna(0)
        .reset_index()
    )
    dist.columns = ["nivel", "qtd"]
    dist = dist[dist["qtd"] > 0]

    if dist.empty:
        st.info("Sem dados para o filtro selecionado.")
    else:
        fig_donut = go.Figure(go.Pie(
            labels=dist["nivel"],
            values=dist["qtd"],
            hole=0.58,
            marker_colors=[CORES.get(v, "#ccc") for v in dist["nivel"]],
            textinfo="percent+label",
            textfont_size=12,
            showlegend=False,
        ))
        fig_donut.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)

with col2:
    st.subheader("Top 10 Disciplinas — % Satisfação")

    sat_disc = df.groupby("DISCIPLINA")["SATISFEITO"].agg(["sum", "count"]).reset_index()
    sat_disc["pct"] = sat_disc["sum"] / sat_disc["count"] * 100
    sat_disc = sat_disc[sat_disc["count"] >= 17]
    sat_disc = sat_disc.nlargest(10, "pct")

    if sat_disc.empty:
        st.info("Sem dados suficientes para o filtro selecionado.")
    else:
        sat_disc["label"] = sat_disc["DISCIPLINA"].str[:55]
        fig_disc = px.bar(
            sat_disc,
            x="pct",
            y="label",
            orientation="h",
            text=sat_disc["pct"].apply(lambda v: f"{v:.1f}%"),
            color="pct",
            color_continuous_scale=["#D85A30", "#EF9F27", "#1D9E75"],
            range_color=[70, 100],
        )
        fig_disc.update_layout(
            height=380,
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            xaxis_title="% satisfação",
            yaxis_title="",
            margin=dict(t=10, b=10, l=10, r=10),
        )
        fig_disc.update_traces(textposition="outside")
        st.plotly_chart(fig_disc, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# LINHA 2: SATISFAÇÃO POR DIMENSÃO
# ─────────────────────────────────────────────────────────────
st.subheader("📐 Índice de Satisfação por Dimensão Avaliada")

sat_dim = df.groupby("PERGUNTA")["SATISFEITO"].agg(["sum", "count"]).reset_index()
sat_dim["pct"] = sat_dim["sum"] / sat_dim["count"] * 100
sat_dim = sat_dim.sort_values("pct", ascending=True)

if sat_dim.empty:
    st.info("Sem dados para o filtro selecionado.")
else:
    fig_dim = px.bar(
        sat_dim,
        x="pct",
        y="PERGUNTA",
        orientation="h",
        text=sat_dim["pct"].apply(lambda v: f"{v:.1f}%"),
        color="pct",
        color_continuous_scale=["#A32D2D", "#D85A30", "#EF9F27", "#1D9E75"],
        range_color=[75, 100],
    )
    fig_dim.update_layout(
        height=500,
        coloraxis_showscale=False,
        xaxis_title="% satisfação",
        yaxis_title="",
        margin=dict(t=10, b=10, l=10, r=10),
    )
    fig_dim.update_traces(textposition="outside")
    st.plotly_chart(fig_dim, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# LINHA 3: EVOLUÇÃO TEMPORAL + PONTOS CRÍTICOS
# ─────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Evolução de Questionários por Dia")

    serie = (
        df.groupby("DATA_DIA")["PESQUISA_COMPLETADO_ID"]
        .nunique()
        .reset_index()
        .rename(columns={"PESQUISA_COMPLETADO_ID": "questionarios"})
    )
    serie = serie[serie["DATA_DIA"].notna()].sort_values("DATA_DIA")

    if serie.empty:
        st.info("Sem dados de data disponíveis.")
    else:
        fig_line = px.line(
            serie, x="DATA_DIA", y="questionarios",
            markers=True,
            labels={"DATA_DIA": "Data", "questionarios": "Questionários"},
        )
        fig_line.update_traces(line_color="#378ADD", marker_color="#378ADD")
        fig_line.update_layout(height=350, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_line, use_container_width=True)

with col4:
    st.subheader("🚨 Pontos Críticos — % Insatisfação por Dimensão")

    insat_dim = df.groupby("PERGUNTA")["INSATISFEITO"].agg(["sum", "count"]).reset_index()
    insat_dim["pct"] = insat_dim["sum"] / insat_dim["count"] * 100
    insat_dim = insat_dim.nlargest(8, "pct").sort_values("pct")

    if insat_dim.empty:
        st.info("Sem dados para o filtro selecionado.")
    else:
        fig_alert = px.bar(
            insat_dim,
            x="pct",
            y="PERGUNTA",
            orientation="h",
            text=insat_dim["pct"].apply(lambda v: f"{v:.1f}%"),
            color="pct",
            color_continuous_scale=["#EF9F27", "#D85A30", "#A32D2D"],
        )
        fig_alert.update_layout(
            height=350,
            coloraxis_showscale=False,
            xaxis_title="% insatisfação",
            yaxis_title="",
            margin=dict(t=10, b=10, l=10, r=10),
        )
        fig_alert.update_traces(textposition="outside")
        st.plotly_chart(fig_alert, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# LINHA 4: HEATMAP
# ─────────────────────────────────────────────────────────────
st.subheader("🔥 Heatmap — Dimensão × Nível de Satisfação (%)")

heat = df.groupby(["PERGUNTA", "VALOR_SELECIONADO"]).size().reset_index(name="qtd")

if heat.empty:
    st.info("Sem dados para o filtro selecionado.")
else:
    heat_piv = heat.pivot(index="PERGUNTA", columns="VALOR_SELECIONADO", values="qtd").fillna(0)
    cols_presentes = [c for c in ORDEM_ESCALA if c in heat_piv.columns]
    heat_piv = heat_piv.reindex(columns=cols_presentes, fill_value=0)
    heat_pct = heat_piv.div(heat_piv.sum(axis=1), axis=0) * 100

    fig_heat = px.imshow(
        heat_pct,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale=["#A32D2D", "#EF9F27", "#1D9E75"],
        zmin=0,
        zmax=100,
    )
    fig_heat.update_layout(
        height=520,
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_colorbar=dict(title="%"),
        xaxis_title="Nível de satisfação",
        yaxis_title="Dimensão avaliada",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# LINHA 5: TABELA DETALHADA COM EXPORT
# ─────────────────────────────────────────────────────────────
st.subheader("📋 Dados Detalhados")

with st.expander("Ver e exportar dados filtrados"):
    tabela = (
        df[["SEMESTRE", "NOME", "RA", "DISCIPLINA", "PERGUNTA", "VALOR_SELECIONADO", "DATA_DIA"]]
        .rename(columns={
            "SEMESTRE": "Semestre",
            "NOME": "Aluno",
            "RA": "RA",
            "DISCIPLINA": "Disciplina",
            "PERGUNTA": "Dimensão",
            "VALOR_SELECIONADO": "Resposta",
            "DATA_DIA": "Data",
        })
        .reset_index(drop=True)
    )

    busca = st.text_input("🔍 Buscar aluno ou disciplina")
    if busca:
        mask = (
            tabela["Aluno"].str.contains(busca, case=False, na=False)
            | tabela["Disciplina"].str.contains(busca, case=False, na=False)
        )
        tabela = tabela[mask]

    st.dataframe(tabela, use_container_width=True, height=400)

    csv_bytes = tabela.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 Exportar CSV",
        data=csv_bytes,
        file_name="satisfacao_filtrada.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "UniAteneu · Projeto de Extensão — Inovação Tecnológica Aplicada ao Mercado · 2026 | "
    "Desenvolvido por Carlos Eduardo Rodrigues Ferreira"
)
