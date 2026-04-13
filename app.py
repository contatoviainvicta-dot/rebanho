import streamlit as st
import pandas as pd
from database import *


import streamlit as st
st.write("App rodando")

# Criar tabelas
criar_tabelas()

st.set_page_config(page_title="Gestão de Rebanho", layout="centered")

st.title("🐄 Gestão de Rebanho - v3.1")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Cadastrar Lote",
        "Cadastrar Animal",
        "Registrar Pesagem",
        "Analisar por Lote",
        "Analisar Animal"
    ]
)

# ---------------------------
# CADASTRAR LOTE
# ---------------------------
if menu == "Cadastrar Lote":
    st.subheader("Novo Lote")

    nome = st.text_input("Nome do lote")
    descricao = st.text_area("Descrição")
    data = st.date_input("Data")

    qtd_comprada = st.number_input("Quantidade comprada", 0)
    qtd_recebida = st.number_input("Quantidade recebida", 0)
    transporte = st.text_input("Tipo de transporte")

    if st.button("Salvar Lote"):
        if not nome:
            st.error("Informe o nome do lote")

        elif qtd_recebida > qtd_comprada:
            st.error("Quantidade recebida não pode ser maior que a comprada")

        elif qtd_recebida == 0:
            st.error("Informe a quantidade recebida")

        else:
            adicionar_lote(
                nome,
                descricao,
                str(data),
                qtd_comprada,
                qtd_recebida,
                transporte
            )

            perda = qtd_comprada - qtd_recebida
            st.success("Lote criado com sucesso!")

            if perda > 0:
                st.warning(f"⚠️ Perda no transporte: {perda} animais")

# ---------------------------
# CADASTRAR ANIMAL
# ---------------------------
elif menu == "Cadastrar Animal":
    st.subheader("Novo Animal")

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Cadastre um lote primeiro")

    else:
        dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

        escolha = st.selectbox("Lote", list(dict_lotes.keys()))
        lote_id = dict_lotes[escolha]

        # 🔥 buscar dados do lote
        lote = obter_lote(lote_id)
        qtd_recebida = lote[5]

        total_animais = contar_animais_no_lote(lote_id)

        st.info(f"🐄 Animais cadastrados: {total_animais} / {qtd_recebida}")

        # BLOQUEIO DE LIMITE
        if total_animais >= qtd_recebida:
            st.error("⚠️ Limite do lote atingido")

        else:
            identificacao = st.text_input("Identificação do animal")
            idade = st.number_input("Idade (meses)", 0, 240)

            if st.button("Salvar Animal"):
                if not identificacao:
                    st.error("Informe a identificação")

                else:
                    adicionar_animal(identificacao, idade, lote_id)
                    st.success("Animal cadastrado com sucesso!")

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

            if peso <= 0:
                st.error("Informe um peso válido")

            elif peso > 1000:
                st.error("Peso muito alto — verificar valor")

            else:
                adicionar_pesagem(animal_id, peso, str(data))
                st.success("Pesagem registrada!")

# ---------------------------
# ANÁLISE POR LOTE
# ---------------------------
elif menu == "Analisar por Lote":
    st.subheader("Análise por Lote")

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Nenhum lote cadastrado")

    else:
        dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

        escolha = st.selectbox("Selecione o lote", list(dict_lotes.keys()))
        lote_id = dict_lotes[escolha]

        lote = obter_lote(lote_id)

        qtd_comprada = lote[4]
        qtd_recebida = lote[5]

        perda = qtd_comprada - qtd_recebida

        st.write(f"📦 Comprados: {qtd_comprada}")
        st.write(f"📥 Recebidos: {qtd_recebida}")

        if perda > 0:
            st.warning(f"⚠️ Perda no transporte: {perda}")

        animais = listar_animais_por_lote(lote_id)

        st.write(f"🐄 Animais cadastrados: {len(animais)}")

        if len(animais) > 0:
            df_animais = pd.DataFrame(
                animais,
                columns=["ID", "Identificação", "Idade", "Lote"]
            )
            st.dataframe(df_animais)

# ---------------------------
# ANÁLISE INDIVIDUAL
# ---------------------------
elif menu == "Analisar Animal":
    st.subheader("Análise do Animal")

    animais = listar_animais()

    if len(animais) == 0:
        st.warning("Nenhum animal cadastrado")

    else:
        dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

        escolha = st.selectbox("Selecione o animal", list(dict_animais.keys()))
        animal_id = dict_animais[escolha]

        pesagens = listar_pesagens(animal_id)

        if len(pesagens) > 0:
            df = pd.DataFrame(
                pesagens,
                columns=["ID", "Animal", "Peso", "Data"]
            )

            df["Data"] = pd.to_datetime(df["Data"])
            df = df.sort_values("Data")

            st.dataframe(df)

            st.subheader("📈 Evolução de Peso")
            st.line_chart(df.set_index("Data")["Peso"])

            # INSIGHT
            if len(df) > 1:
                ganho = df["Peso"].diff().mean()

                st.write(f"📊 Ganho médio: {ganho:.2f} kg/dia")

                if ganho < 0.3:
                    st.warning("⚠️ Baixo ganho de peso")
                else:
                    st.success("✅ Ganho adequado")

        else:
            st.info("Sem pesagens registradas")
