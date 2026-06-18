import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from graphviz import Digraph
from datetime import datetime
from PIL import Image
import pytesseract
import re

st.set_page_config(page_title="GMC BPMN", layout="wide")

st.title("🏗️ BPMN - Recebimento de Mercadorias GMC")

if "historico" not in st.session_state:
    st.session_state.historico = []

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Visualizar BPMN",
        "Novo Recebimento com XML",
        "Recebimento por Foto da NF",
        "Histórico"
    ]
)

def ler_xml_nfe(arquivo):
    tree = ET.parse(arquivo)
    root = tree.getroot()
    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

    ide = root.find(".//nfe:ide", ns)
    emit = root.find(".//nfe:emit", ns)
    total = root.find(".//nfe:ICMSTot", ns)

    dados = {
        "numero_nf": ide.findtext("nfe:nNF", default="", namespaces=ns) if ide is not None else "",
        "data_nf": ide.findtext("nfe:dhEmi", default="", namespaces=ns) if ide is not None else "",
        "fornecedor": emit.findtext("nfe:xNome", default="", namespaces=ns) if emit is not None else "",
        "cnpj": emit.findtext("nfe:CNPJ", default="", namespaces=ns) if emit is not None else "",
        "valor_total": total.findtext("nfe:vNF", default="", namespaces=ns) if total is not None else "",
        "produtos": []
    }

    for det in root.findall(".//nfe:det", ns):
        prod = det.find("nfe:prod", ns)
        if prod is not None:
            dados["produtos"].append({
                "Código": prod.findtext("nfe:cProd", default="", namespaces=ns),
                "Produto": prod.findtext("nfe:xProd", default="", namespaces=ns),
                "Quantidade": prod.findtext("nfe:qCom", default="", namespaces=ns),
                "Unidade": prod.findtext("nfe:uCom", default="", namespaces=ns),
                "Valor Unitário": prod.findtext("nfe:vUnCom", default="", namespaces=ns),
                "Valor Total": prod.findtext("nfe:vProd", default="", namespaces=ns),
            })

    return dados

def extrair_texto_imagem(imagem):
    texto = pytesseract.image_to_string(imagem, lang="por")
    return texto

def buscar_cnpj(texto):
    padrao = r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}"
    achou = re.search(padrao, texto)
    return achou.group(0) if achou else ""

def buscar_numero_nf(texto):
    padroes = [
        r"N[ºoO]?\s*\.?\s*(\d{3,})",
        r"NF[-\s]?e\s*(\d{3,})",
        r"Nota Fiscal\s*(\d{3,})"
    ]
    for p in padroes:
        achou = re.search(p, texto, re.IGNORECASE)
        if achou:
            return achou.group(1)
    return ""

def buscar_data(texto):
    padrao = r"\d{2}/\d{2}/\d{4}"
    achou = re.search(padrao, texto)
    return achou.group(0) if achou else ""

def buscar_valor(texto):
    padrao = r"R\$\s*\d+[.,]\d{2}"
    achou = re.search(padrao, texto)
    return achou.group(0) if achou else ""

if menu == "Visualizar BPMN":
    st.header("Fluxo TO-BE com XML e Foto da NF")

    dot = Digraph()
    dot.attr(rankdir="LR")

    dot.node("A", "Início", shape="circle")
    dot.node("B", "Receber NF\nXML ou Foto", shape="box")
    dot.node("C", "Sistema extrai dados", shape="box")
    dot.node("D", "Funcionário valida", shape="box")
    dot.node("E", "Conferir mercadorias", shape="box")
    dot.node("F", "Mercadoria correta?", shape="diamond")
    dot.node("G", "Registrar divergência", shape="box")
    dot.node("H", "Contatar fornecedor", shape="box")
    dot.node("I", "Entrada no ERP", shape="box")
    dot.node("J", "Etiquetar produtos", shape="box")
    dot.node("K", "Destino?", shape="diamond")
    dot.node("L", "Estoque", shape="box")
    dot.node("M", "Exposição", shape="box")
    dot.node("N", "Fim", shape="doublecircle")

    dot.edges([("A","B"),("B","C"),("C","D"),("D","E"),("E","F")])
    dot.edge("F","G",label="Não")
    dot.edge("G","H")
    dot.edge("H","N")
    dot.edge("F","I",label="Sim")
    dot.edge("I","J")
    dot.edge("J","K")
    dot.edge("K","L",label="Estoque")
    dot.edge("K","M",label="Exposição")
    dot.edge("L","N")
    dot.edge("M","N")

    st.graphviz_chart(dot)

elif menu == "Novo Recebimento com XML":
    st.header("Novo Recebimento com XML da NF-e")

    arquivo_xml = st.file_uploader("Envie o XML da NF-e", type=["xml"])

    if arquivo_xml is not None:
        try:
            dados_xml = ler_xml_nfe(arquivo_xml)
            st.success("XML lido com sucesso!")

            col1, col2 = st.columns(2)

            with col1:
                fornecedor = st.text_input("Fornecedor", dados_xml["fornecedor"])
                numero_nf = st.text_input("Número da NF", dados_xml["numero_nf"])
                cnpj = st.text_input("CNPJ", dados_xml["cnpj"])

            with col2:
                data_nf = st.text_input("Data da NF", dados_xml["data_nf"])
                valor_total = st.text_input("Valor total da NF", dados_xml["valor_total"])
                responsavel = st.text_input("Responsável pelo recebimento")

            st.subheader("Produtos da NF")
            df_produtos = pd.DataFrame(dados_xml["produtos"])
            st.dataframe(df_produtos, use_container_width=True)

            mercadoria_recebida = st.checkbox("Mercadoria recebida")
            quantidade_conferida = st.checkbox("Quantidade conferida")
            avarias_verificadas = st.checkbox("Avarias verificadas")
            entrada_erp = st.checkbox("Entrada no ERP realizada")
            produtos_etiquetados = st.checkbox("Produtos etiquetados")

            destino = st.selectbox("Destino principal", ["Estoque", "Exposição", "Estoque e Exposição"])
            divergencia = st.radio("Houve divergência?", ["Não", "Sim"])
            observacoes = st.text_area("Observações / divergências encontradas")

            if st.button("Salvar Recebimento XML"):
                registro = {
                    "Data registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Tipo": "XML",
                    "Fornecedor": fornecedor,
                    "NF": numero_nf,
                    "CNPJ": cnpj,
                    "Data NF": data_nf,
                    "Valor total": valor_total,
                    "Responsável": responsavel,
                    "Mercadoria recebida": mercadoria_recebida,
                    "Quantidade conferida": quantidade_conferida,
                    "Avarias verificadas": avarias_verificadas,
                    "Entrada ERP": entrada_erp,
                    "Produtos etiquetados": produtos_etiquetados,
                    "Destino": destino,
                    "Divergência": divergencia,
                    "Observações": observacoes,
                    "Qtd. itens NF": len(dados_xml["produtos"])
                }

                st.session_state.historico.append(registro)
                st.success("Recebimento salvo com sucesso!")

        except Exception as e:
            st.error("Não foi possível ler o XML.")
            st.exception(e)

elif menu == "Recebimento por Foto da NF":
    st.header("📷 Recebimento por Foto da NF")

    st.warning("A leitura por foto pode ter erros. Sempre confira os dados antes de salvar.")

    opcao = st.radio(
        "Como deseja enviar a imagem?",
        ["Tirar foto pelo celular/câmera", "Enviar imagem"]
    )

    imagem = None

    if opcao == "Tirar foto pelo celular/câmera":
        imagem = st.camera_input("Tire a foto da nota fiscal")
    else:
        imagem = st.file_uploader("Envie uma imagem da NF", type=["jpg", "jpeg", "png"])

    if imagem is not None:
        img = Image.open(imagem)
        st.image(img, caption="Imagem enviada", use_container_width=True)

        with st.spinner("Lendo a imagem..."):
            texto_extraido = extrair_texto_imagem(img)

        st.subheader("Texto extraído da imagem")
        st.text_area("Resultado do OCR", texto_extraido, height=250)

        cnpj_sugerido = buscar_cnpj(texto_extraido)
        nf_sugerida = buscar_numero_nf(texto_extraido)
        data_sugerida = buscar_data(texto_extraido)
        valor_sugerido = buscar_valor(texto_extraido)

        st.subheader("Dados identificados automaticamente")

        col1, col2 = st.columns(2)

        with col1:
            fornecedor = st.text_input("Fornecedor", "")
            numero_nf = st.text_input("Número da NF", nf_sugerida)
            cnpj = st.text_input("CNPJ", cnpj_sugerido)

        with col2:
            data_nf = st.text_input("Data da NF", data_sugerida)
            valor_total = st.text_input("Valor total", valor_sugerido)
            responsavel = st.text_input("Responsável pelo recebimento")

        st.subheader("Checklist de Recebimento")

        mercadoria_recebida = st.checkbox("Mercadoria recebida")
        quantidade_conferida = st.checkbox("Quantidade conferida")
        avarias_verificadas = st.checkbox("Avarias verificadas")
        entrada_erp = st.checkbox("Entrada no ERP realizada")
        produtos_etiquetados = st.checkbox("Produtos etiquetados")

        destino = st.selectbox("Destino principal", ["Estoque", "Exposição", "Estoque e Exposição"])
        divergencia = st.radio("Houve divergência?", ["Não", "Sim"])
        observacoes = st.text_area("Observações / divergências encontradas")

        if st.button("Salvar Recebimento por Foto"):
            registro = {
                "Data registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Tipo": "Foto",
                "Fornecedor": fornecedor,
                "NF": numero_nf,
                "CNPJ": cnpj,
                "Data NF": data_nf,
                "Valor total": valor_total,
                "Responsável": responsavel,
                "Mercadoria recebida": mercadoria_recebida,
                "Quantidade conferida": quantidade_conferida,
                "Avarias verificadas": avarias_verificadas,
                "Entrada ERP": entrada_erp,
                "Produtos etiquetados": produtos_etiquetados,
                "Destino": destino,
                "Divergência": divergencia,
                "Observações": observacoes
            }

            st.session_state.historico.append(registro)
            st.success("Recebimento por foto salvo com sucesso!")

elif menu == "Histórico":
    st.header("Histórico de Recebimentos")

    if len(st.session_state.historico) == 0:
        st.info("Nenhum recebimento registrado ainda.")
    else:
        df = pd.DataFrame(st.session_state.historico)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "Baixar histórico em CSV",
            csv,
            "historico_recebimentos_gmc.csv",
            "text/csv"
        )
