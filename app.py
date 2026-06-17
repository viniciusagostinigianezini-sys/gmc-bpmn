import streamlit as st
import pandas as pd
from graphviz import Digraph
from datetime import datetime

st.set_page_config(page_title="GMC BPMN", layout="wide")

st.title("🏗️ BPMN - GMC Materiais de Construção")

# Inicializa histórico
if "historico" not in st.session_state:
    st.session_state.historico = []

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Visualizar BPMN",
        "Novo Recebimento",
        "Histórico"
    ]
)

# ================= BPMN =================
if menu == "Visualizar BPMN":

    st.header("Fluxo de Recebimento")

    dot = Digraph()
    dot.attr(rankdir="LR")

    dot.node("A", "Início", shape="circle")
    dot.node("B", "Receber mercadorias", shape="box")
    dot.node("C", "Conferir produtos", shape="box")
    dot.node("D", "Mercadoria correta?", shape="diamond")
    dot.node("E", "Registrar divergência", shape="box")
    dot.node("F", "Etiquetar produtos", shape="box")
    dot.node("G", "Entrada no ERP", shape="box")
    dot.node("H", "Estoque ou Exposição?", shape="diamond")
    dot.node("I", "Armazenar estoque", shape="box")
    dot.node("J", "Expor na loja", shape="box")
    dot.node("K", "Fim", shape="doublecircle")

    dot.edges([("A","B"),("B","C"),("C","D")])
    dot.edge("D","E",label="Não")
    dot.edge("E","K")
    dot.edge("D","F",label="Sim")
    dot.edge("F","G")
    dot.edge("G","H")
    dot.edge("H","I",label="Estoque")
    dot.edge("H","J",label="Exposição")
    dot.edge("I","K")
    dot.edge("J","K")

    st.graphviz_chart(dot)

# ================= NOVO RECEBIMENTO =================
elif menu == "Novo Recebimento":

    st.header("Novo Recebimento")

    fornecedor = st.text_input("Fornecedor")
    nf = st.text_input("Número da NF")
    responsavel = st.text_input("Responsável")

    conferencia = st.checkbox("Produtos conferidos")
    etiquetado = st.checkbox("Produtos etiquetados")
    erp = st.checkbox("Entrada no ERP realizada")

    destino = st.selectbox(
        "Destino",
        ["Estoque", "Exposição"]
    )

    observacoes = st.text_area("Observações")

    if st.button("Salvar Recebimento"):

        registro = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Fornecedor": fornecedor,
            "NF": nf,
            "Responsável": responsavel,
            "Conferência": conferencia,
            "Etiquetado": etiquetado,
            "ERP": erp,
            "Destino": destino,
            "Observações": observacoes
        }

        st.session_state.historico.append(registro)

        st.success("Recebimento salvo com sucesso!")

# ================= HISTÓRICO =================
elif menu == "Histórico":

    st.header("Histórico")

    if len(st.session_state.historico) == 0:
        st.info("Nenhum recebimento registrado.")
    else:
        df = pd.DataFrame(st.session_state.historico)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Baixar CSV",
            csv,
            "historico_recebimentos.csv",
            "text/csv"
        )
