import streamlit as st
from graphviz import Digraph

st.set_page_config(page_title="BPMN GMC", layout="wide")

st.title("🏗️ BPMN - GMC Materiais de Construção")

processo = st.selectbox(
    "Escolha um processo:",
    [
        "Recebimento de Mercadorias",
        "Venda no Balcão"
    ]
)

dot = Digraph()
dot.attr(rankdir="LR")

if processo == "Recebimento de Mercadorias":

    dot.node("A", "Início", shape="circle")
    dot.node("B", "Receber mercadorias", shape="box")
    dot.node("C", "Conferir produtos", shape="box")
    dot.node("D", "Mercadoria correta?", shape="diamond")
    dot.node("E", "Contatar fornecedor", shape="box")
    dot.node("F", "Etiquetar produtos", shape="box")
    dot.node("G", "Entrada no ERP", shape="box")
    dot.node("H", "Estoque ou Exposição?", shape="diamond")
    dot.node("I", "Armazenar estoque", shape="box")
    dot.node("J", "Expor na loja", shape="box")
    dot.node("K", "Fim", shape="doublecircle")

    dot.edges([("A","B"),("B","C"),("C","D")])

    dot.edge("D", "E", label="Não")
    dot.edge("E", "K")

    dot.edge("D", "F", label="Sim")
    dot.edge("F", "G")
    dot.edge("G", "H")

    dot.edge("H", "I", label="Estoque")
    dot.edge("H", "J", label="Exposição")

    dot.edge("I", "K")
    dot.edge("J", "K")

else:

    dot.node("A", "Cliente chega", shape="circle")
    dot.node("B", "Atender cliente", shape="box")
    dot.node("C", "Consultar estoque", shape="box")
    dot.node("D", "Produto disponível?", shape="diamond")
    dot.node("E", "Encomendar produto", shape="box")
    dot.node("F", "Gerar orçamento", shape="box")
    dot.node("G", "Cliente aprovou?", shape="diamond")
    dot.node("H", "Emitir venda", shape="box")
    dot.node("I", "Separar mercadoria", shape="box")
    dot.node("J", "Fim", shape="doublecircle")

    dot.edges([("A","B"),("B","C"),("C","D")])

    dot.edge("D", "E", label="Não")
    dot.edge("E", "J")

    dot.edge("D", "F", label="Sim")
    dot.edge("F", "G")

    dot.edge("G", "J", label="Não")
    dot.edge("G", "H", label="Sim")

    dot.edge("H", "I")
    dot.edge("I", "J")

st.graphviz_chart(dot)
