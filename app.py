import streamlit as st
import pandas as pd
from database import *

# Criar tabela
criar_tabela()

st.set_page_config(page_title="Gestão de Rebanho", layout="centered")

st.title("🐄 Gestão de Rebanho - MVP")

menu = st.sidebar.selectbox("Menu", ["Cadastrar Animal", "Visualizar Dados"])

# -------------------------------
# CADASTRO
# -------------------------------
if menu == "Cadastrar Animal":
    st.subheader("Cadastro de Animal")

    identificacao = st.text_input("Identificação (ex: Brinco 001)")
    idade = st.number_input("Idade (meses)", min_value=0, max_value=240)
    peso = st.number_input("Peso (kg)", min_value=0.0)
    data = st.date_input("Data da pesagem")

    if st.button("Salvar"):
        if identificacao != "":
            adicionar_animal(identificacao, idade, peso, str(data))
            st.success("✅ Animal cadastrado com sucesso!")
        else:
            st.error("⚠️ Informe a identificação")

# -------------------------------
# VISUALIZAÇÃO
# -------------------------------
if menu == "Visualizar Dados":
    st.subheader("Dados do Rebanho")

    dados = listar_animais()

    if len(dados) > 0:
        df = pd.DataFrame(dados, columns=["ID", "Identificação", "Idade", "Peso", "Data"])

        st.dataframe(df)

        st.subheader("📈 Evolução de Peso")

        # Converter data
        df["Data"] = pd.to_datetime(df["Data"])

        df = df.sort_values("Data")

        st.line_chart(df.set_index("Data")["Peso"])

        # ALERTA SIMPLES
        peso_medio = df["Peso"].mean()

        if peso_medio < 200:
            st.warning("⚠️ Peso médio baixo — avaliar manejo alimentar")
        else:
            st.success("✅ Peso médio adequado")

    else:
        st.info("Nenhum dado cadastrado ainda.")
