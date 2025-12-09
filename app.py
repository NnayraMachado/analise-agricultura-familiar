# ================================================================
# APP FINAL — AGRICULTURA FAMILIAR & IMPACTOS DO ROMPIMENTO
# ================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------
# CONFIGURAÇÃO DO APP
# ----------------------------------------------------------
st.set_page_config(
    page_title="Análise Agricultura Familiar",
    layout="wide",
    page_icon="🌱"
)

FILE_PATH = r"C:\Users\nirva\OneDrive\Área de Trabalho\Adai\DADOS\DADOS-AGRICULTURA_FAMILIAR\AGRICULTURA_FAMILIAR.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(FILE_PATH)

df = load_data()

# ================================================================
# TRATAMENTO DE VARIÁVEIS SENSÍVEIS
# ================================================================
variaveis_sensiveis = [
    "ID1 - Nome completo/nome social do(a) informante do núcleo familiar:",
    "ID3 - Qual sua data de nascimento?"
]

def coluna_e_categorica(col):
    return df[col].nunique() <= 20

variaveis_plotaveis = [
    col for col in df.columns
    if col not in variaveis_sensiveis and coluna_e_categorica(col)
]

# ================================================================
# DEFINIÇÃO DOS PARES ANTES × DEPOIS
# ================================================================
pares_comparativos = {
    # Grupo 1 – Recursos naturais
    "ADAI_PCT4.1 - QUAIS RECURSOS NATURAIS eram utilizados por você e sua comunidade?":
        "ADAI_PCT4.3.1 - QUAIS RECURSOS NATURAIS você e sua comunidade deixaram de utilizar?",

    # Grupo 2 – Uso da Água
    "ADAI_AQA1 - ANTES do rompimento da Barragem de Fundão, no dia 5 de novembro de 2015, de propriedade das empresas Samarco, Vale e BHP Billiton, você e/ou seu núcleo familiar utilizavam o mar (oceano)?":
        "AQA2 - Atualmente você e/ou seu núcleo familiar fazem uso doméstico da água do Rio Doce e afluentes?",

    # Grupo 3 – Fontes de Abastecimento
    "AQA4 - ANTES do rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton, qual(ais) a(s) fonte(s) de abastecimento de água utilizada(s)?":
        "AQA5 - Atualmente qual(ais) é/são a(s) fonte(s) de abastecimento de água utilizada(s)?",

    # Grupo 4 – Subsistência
    "ARF1 - ANTES do rompimento da barragem de fundão, de propriedade das empresas Samarco, vale e BHP Billiton, você e/ou seu núcleo familiar realizavam alguma dessas atividades de subsistência:":
        "ARF1.3 - DEVIDO ao rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton, as atividades de subsistência desempenhadas por você e/ou seu núcleo familiar foram ALTERADAS?",

    # Grupo 5 – Atividade Remunerada
    "AER1.1.1.2 - Qual profissão você exercia na atividade remunerada?":
        "AER1.1.1.3 - Atualmente você continua a exercer essa mesma atividade remunerada?",
}

# ================================================================
# FUNÇÕES DE GRÁFICOS
# ================================================================

def limitar_categorias(col):
    vc = df[col].value_counts()
    if len(vc) > 12:
        top10 = vc.head(10)
        outros = vc.iloc[10:].sum()
        top10["Outros"] = outros
        return top10
    return vc

def grafico_barras(col):
    freq = limitar_categorias(col).sort_values()
    fig = px.bar(
        freq,
        orientation='h',
        labels={'value': 'Frequência', 'index': col},
        text_auto=True,
        title=col
    )
    st.plotly_chart(fig, use_container_width=True)
    return fig

def grafico_pizza(col):
    freq = limitar_categorias(col)
    if len(freq) > 7:
        st.warning("Muitas categorias para pizza. Usando barras horizontais.")
        return grafico_barras(col)
    fig = px.pie(
        values=freq.values,
        names=freq.index,
        title=col,
        hole=.4
    )
    st.plotly_chart(fig, use_container_width=True)
    return fig

def grafico_comparativo(col_antes, col_depois):
    fa = df[col_antes].value_counts()
    fd = df[col_depois].value_counts()

    categorias = list(set(fa.index).union(fd.index))

    antes_vals = [fa.get(cat, 0) for cat in categorias]
    depois_vals = [fd.get(cat, 0) for cat in categorias]

    fig = go.Figure()
    fig.add_bar(name="Antes", x=antes_vals, y=categorias, orientation="h")
    fig.add_bar(name="Depois", x=depois_vals, y=categorias, orientation="h")

    fig.update_layout(
        barmode="group",
        title=f"{col_antes}  ×  {col_depois}",
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)
    return fig

# ================================================================
# ANÁLISE TÉCNICA AUTOMÁTICA
# ================================================================
def analise_tecnica(col):
    freq = df[col].value_counts(normalize=True) * 100
    freq = freq.round(2)

    st.subheader("📘 Análise Técnica")
    st.markdown(f"""
**Variável analisada:** `{col}`  
Total de respostas válidas: **{df[col].notna().sum()}**

### Distribuição percentual:
{freq.to_frame("Percentual (%)").to_markdown()}
""")

def analise_tecnica_comparativo(col1, col2):
    st.subheader("📘 Análise Técnica – Comparativo")
    st.markdown(f"""
**Antes:** `{col1}`  
**Depois:** `{col2}`  

### Interpretação:
- Mudanças expressas representam tendências percebidas pelos entrevistados.  
- Diferenças entre distribuições indicam impacto na vida dos atingidos.  
- Não há inferência causal, apenas descritiva.  
""")

# ================================================================
# DASHBOARD INICIAL
# ================================================================
def dashboard_inicial():
    st.header("📊 Visão Geral dos Entrevistados")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de entrevistados", len(df))
    col2.metric("Variáveis disponíveis", len(df.columns))
    col3.metric("Territórios distintos", df["ADAI_CT4 - O território ao qual pertence o entrevistado está em qual dessas localidades?"].nunique())

    st.subheader("Distribuição por Território")
    freq = df["ADAI_CT4 - O território ao qual pertence o entrevistado está em qual dessas localidades?"].value_counts()
    st.plotly_chart(px.bar(freq, text_auto=True), use_container_width=True)

# ================================================================
# HISTÓRICO DE DANOS
# ================================================================
def dashboard_danos():
    st.header("⚠ Histórico de Danos")

    danos_cols = [
        "AQA6 - DEVIDO ao rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton, você e/ou seu núcleo familiar avaliam que houve alguma alteração na qualidade da água acessada para uso doméstico?",
        "SA1 - Devido ao rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton, você e/ou seu núcleo familiar avaliam que houve comprometimento da QUALIDADE de alimentos?",
        "SA3 - DEVIDO ao rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton, houve diminuição na QUANTIDADE de alimentos que você e/ou seu núcleo familiar tinham acesso?",
        "CCS7 - Devido ao rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton, você e/ou seu núcleo familiar avaliam que houve um aumento de gastos com a saúde?"
    ]

    freq = {col: df[col].value_counts().get("Sim", 0) for col in danos_cols}

    fig = px.bar(
        x=list(freq.keys()),
        y=list(freq.values()),
        text_auto=True,
        title="Quantidade de danos relatados (respostas SIM)"
    )

    st.plotly_chart(fig, use_container_width=True)

# ================================================================
# INTERFACE DO APP (ABAS)
# ================================================================
menu = st.sidebar.radio(
    "Menu",
    ["Dashboard Inicial", "Variáveis", "Comparativo Antes × Depois", "Histórico de Danos", "Sobre"]
)

if menu == "Dashboard Inicial":
    dashboard_inicial()

elif menu == "Variáveis":
    col = st.selectbox("Selecione uma variável:", variaveis_plotaveis)
    tipo = st.radio("Tipo de gráfico:", ["Barras", "Pizza"])

    if tipo == "Barras":
        fig = grafico_barras(col)
    else:
        fig = grafico_pizza(col)

    analise_tecnica(col)

elif menu == "Comparativo Antes × Depois":
    st.header("🔄 Comparativo Antes × Depois")

    col_antes = st.selectbox("Selecione a variável (ANTES):", list(pares_comparativos.keys()))
    col_depois = pares_comparativos[col_antes]

    grafico_comparativo(col_antes, col_depois)
    analise_tecnica_comparativo(col_antes, col_depois)

elif menu == "Histórico de Danos":
    dashboard_danos()

elif menu == "Sobre":
    st.header("ℹ️ Sobre a Pesquisa")
    st.markdown("""
Este painel apresenta um conjunto de análises produzidas a partir dos dados coletados com famílias atingidas pelo rompimento da Barragem de Fundão, de propriedade das empresas Samarco, Vale e BHP Billiton. O objetivo é compreender, de forma sistemática e transparente, os impactos sociais, econômicos, ambientais, culturais e produtivos vivenciados pelas comunidades ao longo dos últimos anos.

As análises aqui apresentadas foram construídas a partir das respostas fornecidas pelos entrevistados, preservando sua percepção, memória social e experiência direta com as transformações ocorridas no território. O painel busca transformar dados complexos em informações claras, úteis e tecnicamente fundamentadas para subsidiar:

- processos de reparação integral;  
- debates públicos e audiências;  
- produção de provas técnicas;  
- tomada de decisão pela comunidade e por assessorias técnicas;  
- formulação de políticas públicas específicas.

## 🎯 Objetivos da Análise
1. Identificar mudanças antes e depois do rompimento nas dimensões produtivas, sociais, ambientais e culturais.  
2. Mapear percepções, sentimentos e preocupações das famílias sobre a qualidade de vida, acesso a recursos e segurança alimentar.  
3. Quantificar danos e perdas relatadas, classificando-os por tipo, intensidade e frequência.  
4. Evidenciar desigualdades territoriais e sociais a partir de marcadores como gênero, idade, escolaridade e ocupação.  
5. Oferecer indicadores sintetizados que auxiliem análises rápidas e robustas sobre a situação das famílias.

## 🧩 Abordagem Metodológica
O painel utiliza diferentes técnicas de análise:

### ➤ 1. Distribuição de Frequências
Aplicada a perguntas objetivas e categóricas, para identificar padrões de respostas.

### ➤ 2. Comparativos Antes × Depois
Utilizados apenas para variáveis que possuem correspondência temporal, possibilitando observar:
- interrupção de atividades tradicionais;  
- perda de acesso a recursos naturais;  
- mudanças em práticas culturais e subsistência;  
- alterações percebidas na qualidade e quantidade de água;  
- impactos alimentares, econômicos e comunitários.

### ➤ 3. Análises Técnicas Textuais
Cada variável inclui sínteses técnicas para apoiar interpretação dos dados, descrevendo:
- relevância do tema,  
- possíveis impactos,  
- relação com direitos, modos de vida e políticas públicas,  
- limitações e hipóteses analíticas.  

### ➤ 4. Visualizações Interativas
Os gráficos deste painel foram desenvolvidos para permitir:
- zoom,  
- navegação por categorias,  
- detalhes sob demanda,  
- leitura clara de grandes volumes de informação.

Os tipos de gráfico são selecionados conforme o sentido analítico:
- barras horizontais para categorias qualitativas,  
- pizza para poucos grupos,  
- histogramas para distribuições,  
- treemaps para grupos grandes,  
- gráficos comparativos para variáveis pareadas.  

## ⚠️ Cuidados e Considerações
- Os resultados expressam percepções e experiências das famílias entrevistadas — não indicam causalidade direta.  
- A amostra representa os respondentes, e não necessariamente todo o território.  
- Respostas abertas podem conter interpretações pessoais, expressões subjetivas e percepções simbólicas.  
- Dados devem ser analisados junto de informações qualitativas, históricas e territoriais.

## 🔍 Transparência e Reprodutibilidade
O painel foi desenvolvido utilizando:
- Python,  
- Pandas,  
- Plotly,  
- Streamlit.  

Essa estrutura permite auditoria técnica, reprodutibilidade e facilidade de atualização.

## 💡 Finalidade Geral
Este ambiente foi criado para que:

✔ **comunidades** compreendam seus próprios dados;  
✔ **assessorias técnicas** fundamentem análises e relatórios;  
✔ **instituições públicas** utilizem informações precisas em políticas e decisões;  
✔ **pesquisadores** encontrem uma base estruturada para estudos.  

O objetivo central é fortalecer o protagonismo das pessoas atingidas, qualificando o debate público e contribuindo para processos de reparação justa e efetiva.
    """)

