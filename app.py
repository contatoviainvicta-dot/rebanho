import streamlit as st
import pandas as pd
from database import *

criar_tabelas()

st.set_page_config(page_title="Gestão de Rebanho", layout="centered")

st.title("🐄 Gestão de Rebanho - v2.0")

menu = st.sidebar.selectbox(
    "Menu",
    ["Cadastrar Animal", "Registrar Pesagem", "Analisar Animal"]
)

# ---------------------------
# CADASTRAR ANIMAL
# ---------------------------
if menu == "Cadastrar Animal":
    st.subheader("Novo Animal")

    identificacao = st.text_input("Identificação")
    idade = st.number_input("Idade (meses)", 0, 240)

    if st.button("Salvar Animal"):
        if identificacao:
            adicionar_animal(identificacao, idade)
            st.success("Animal cadastrado!")
        else:
            st.error("Informe a identificação")

# ---------------------------
# REGISTRAR PESAGEM
# ---------------------------
elif menu == "Registrar Pesagem":
    st.subheader("Registrar Peso")

    animais = listar_animais()

    if len(animais) == 0:
        st.warning("Cadastre um animal primeiro")
    else:
        dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

        escolha = st.selectbox("Animal", list(dict_animais.keys()))
        animal_id = dict_animais[escolha]

        peso = st.number_input("Peso (kg)", 0.0)
        data = st.date_input("Data")

        if st.button("Salvar Pesagem"):
            if peso > 1000:
                st.error("Peso muito alto — verificar valor")
            elif peso == 0:
                st.error("Informe o peso")
            else:
                adicionar_pesagem(animal_id, peso, str(data))
                st.success("Pesagem registrada!")

# ---------------------------
# ANÁLISE
# ---------------------------
elif menu == "Analisar Animal":
    st.subheader("Análise do Animal")

    animais = listar_animais()

    if len(animais) == 0:
        st.warning("Cadastre um animal primeiro")
    else:
        dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

        escolha = st.selectbox("Selecione o animal", list(dict_animais.keys()))
        animal_id = dict_animais[escolha]

        pesagens = listar_pesagens(animal_id)

        if len(pesagens) > 0:
            df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])

            df["Data"] = pd.to_datetime(df["Data"])
            df = df.sort_values("Data")

            st.dataframe(df)

            st.subheader("📈 Evolução de Peso")
            st.line_chart(df.set_index("Data")["Peso"])

            # INSIGHT
            if len(df) > 1:
                ganho_medio = df["Peso"].diff().mean()

                st.write(f"📊 Ganho médio: {ganho_medio:.2f} kg/dia")

                if ganho_medio < 0.3:
                    st.warning("⚠️ Baixo ganho de peso")
                else:
                    st.success("✅ Ganho adequado")

        else:
            st.info("Sem pesagens registradas")
