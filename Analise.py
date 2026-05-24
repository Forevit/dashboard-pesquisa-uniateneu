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
# MAPEAMENTO DAS 17 PERGUNTAS (posição 0-16 dentro do questionário)
# ─────────────────────────────────────────────────────────────
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
    "Muito satisfeito":       "#1D9E75",
    "Satisfeito":             "#378ADD",
    "Parcialmente satisfeito":"#EF9F27",
    "Insatisfeito":           "#D85A30",
    "Muito insatisfeito":     "#A32D2D",
    "Não sei avaliar":        "#888780",
}

# ─────────────────────────────────────────────────────────────
# CARREGAMENTO E PRÉ-PROCESSAMENTO
# ─────────────────────────────────────────────────────────────
@st.cache_data
def carregar_dados(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df.columns = [c.strip().upper() for c in df.columns]

    # Limpar espaços em VALOR_SELECIONADO
    df["VALOR_SELECIONADO"] = df["VALOR_SELECIONADO"].astype(str).str.strip()

    # Manter apenas multichoice (único tipo presente)
    mc = df[df["ITEM_TIPO"] == "multichoice"].copy()

    # Atribuir número da pergunta (0-16) dentro de cada questionário
    mc = mc.sort_values(["PESQUISA_COMPLETADO_ID", "VALOR_ID"])
    mc["PERGUNTA_N"] = mc.groupby("PESQUISA_COMPLETADO_ID").cumcount()

    # Filtrar apenas as 17 perguntas de satisfação (posições 0-16)
    mc = mc[mc["PERGUNTA_N"] < 17].copy()
    mc["PERGUNTA"] = mc["PERGUNTA_N"].map(lambda n: PERGUNTAS[n])

    # Converter data
    mc["DATA"] = pd.to_datetime(
        mc["PESQUISA_COMPLETADO_DATA_MODIFICACAO"], errors="coerce"
    )
    mc["DATA_DIA"] = mc["DATA"].dt.date

    # Flags de satisfação/insatisfação
    mc["SATISFEITO"] = mc["VALOR_SELECIONADO"].isin(
        ["Muito satisfeito", "Satisfeito"]
    )
    mc["INSATISFEITO"] = mc["VALOR_SELECIONADO"].isin(
        ["Insatisfeito", "Muito insatisfeito"]
    )

    return mc


# ─────────────────────────────────────────────────────────────
# CARREGAMENTO
# ─────────────────────────────────────────────────────────────
CSV_PATH = "baseTratada.csv"

try:
    mc = carregar_dados(CSV_PATH)
except FileNotFoundError:
    st.error(
        f"❌ Arquivo **{CSV_PATH}** não encontrado. "
        "Coloque-o na mesma pasta que este script e tente novamente."
    )
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
st.caption(
    "Projeto de Extensão — Inovação Tecnológica Aplicada ao Mercado · UniAteneu 2025.1.1"
)
st.divider()

# ─────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────
total_alunos        = df["RA"].nunique()
total_questionarios = df["PESQUISA_COMPLETADO_ID"].nunique()
total_respostas     = len(df)
pct_sat             = df["SATISFEITO"].mean() * 100
pct_insat           = df["INSATISFEITO"].mean() * 100
nps                 = (df["SATISFEITO"].mean() - df["INSATISFEITO"].mean()) * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("👥 Alunos únicos",   f"{total_alunos:,}".replace(",", "."))
c2.metric("📋 Questionários",   f"{total_questionarios:,}".replace(",", "."))
c3.metric("📝 Respostas",       f"{total_respostas:,}".replace(",", "."))
c4.metric("✅ Satisfação",      f"{pct_sat:.1f}%")
c5.metric("⚠️ Insatisfação",    f"{pct_insat:.1f}%")
c6.metric("⭐ NPS Educacional", f"{nps:.1f}")

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

    sat_disc = (
        df.groupby("DISCIPLINA")["SATISFEITO"]
        .agg(["sum", "count"])
        .reset_index()
    )
    sat_disc["pct"] = sat_disc["sum"] / sat_disc["count"] * 100
    sat_disc = sat_disc[sat_disc["count"] >= 17]   # ao menos 1 questionário completo
    sat_disc = sat_disc.nlargest(10, "pct")

    if sat_disc.empty:
        st.info("Sem dados suficientes para o filtro selecionado.")
    else:
        # Abreviação do nome da disciplina para o gráfico
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
# LINHA 2: SATISFAÇÃO POR DIMENSÃO (barras horizontais)
# ─────────────────────────────────────────────────────────────
st.subheader("📐 Índice de Satisfação por Dimensão Avaliada")

sat_dim = (
    df.groupby("PERGUNTA")["SATISFEITO"]
    .agg(["sum", "count"])
    .reset_index()
)
sat_dim["pct"] = sat_dim["sum"] / sat_dim["count"] * 100
sat_dim = sat_dim.sort_values("pct", ascending=True)

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
    st.subheader("📈 Evolução de Respostas por Dia")

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
        fig_line.update_layout(
            height=350, margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_line, use_container_width=True)

with col4:
    st.subheader("🚨 Pontos Críticos — % Insatisfação por Dimensão")

    insat_dim = (
        df.groupby("PERGUNTA")["INSATISFEITO"]
        .agg(["sum", "count"])
        .reset_index()
    )
    insat_dim["pct"] = insat_dim["sum"] / insat_dim["count"] * 100
    insat_dim = insat_dim.nlargest(8, "pct").sort_values("pct")

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
# LINHA 4: HEATMAP Dimensão × Nível de Satisfação
# ─────────────────────────────────────────────────────────────
st.subheader("🔥 Heatmap — Dimensão × Nível de Satisfação (%)")

heat = (
    df.groupby(["PERGUNTA", "VALOR_SELECIONADO"])
    .size()
    .reset_index(name="qtd")
)
heat_piv = heat.pivot(
    index="PERGUNTA", columns="VALOR_SELECIONADO", values="qtd"
).fillna(0)

# Reindexar apenas as colunas presentes que são da escala
cols_presentes = [c for c in ORDEM_ESCALA if c in heat_piv.columns]
heat_piv = heat_piv.reindex(columns=cols_presentes, fill_value=0)

# Converter para percentual por linha
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
        df[["SEMESTRE", "NOME", "RA", "DISCIPLINA", "PERGUNTA",
            "VALOR_SELECIONADO", "DATA_DIA"]]
        .rename(columns={
            "SEMESTRE":         "Semestre",
            "NOME":             "Aluno",
            "RA":               "RA",
            "DISCIPLINA":       "Disciplina",
            "PERGUNTA":         "Dimensão",
            "VALOR_SELECIONADO":"Resposta",
            "DATA_DIA":         "Data",
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
    "UniAteneu · Projeto de Extensão — Inovação Tecnológica Aplicada ao Mercado · 2026  |  "
    "Desenvolvido por Carlos Eduardo Rodrigues Ferreira"
)