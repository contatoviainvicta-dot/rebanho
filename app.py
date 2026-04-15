import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    criar_tabelas,
    listar_lotes,
    adicionar_lote,
    obter_lote,
    listar_animais,
    listar_animais_por_lote,
    adicionar_animal,
    contar_animais_no_lote,
    adicionar_pesagem,
    listar_pesagens
)

# Inicializar banco
criar_tabelas()

st.set_page_config(page_title="Gestão de Rebanho", layout="centered")

st.title("🐄 Gestão de Rebanho - v4.0")

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

    preco_por_animal = st.number_input("Preço por animal (R$)", 0.0)

    raca = st.selectbox("Raça", ["Nelore", "Angus", "Cruzamento", "Outros"])
    categoria = st.selectbox("Categoria", ["Bezerro", "Recria", "Engorda"])

    mortalidade = st.number_input("Mortalidade no lote", 0)

    tipo_alimentacao = st.selectbox(
        "Tipo de alimentação",
        ["Pasto", "Confinamento", "Semi-confinamento"]
    )

    tipo_dieta = st.selectbox(
        "Tipo de dieta",
        ["Capim", "Ração", "Silagem", "Misto"]
    )

    custo_total = preco_por_animal * qtd_comprada
    st.info(f"💰 Custo total estimado: R$ {custo_total:.2f}")

    if st.button("Salvar Lote"):

        if not nome:
            st.error("Informe o nome do lote")

        elif qtd_recebida > qtd_comprada:
            st.error("Quantidade recebida não pode ser maior que a comprada")

        elif qtd_recebida == 0:
            st.error("Informe a quantidade recebida")

        else:
            # 🔥 salvar em ISO
            data_iso = data.strftime("%Y-%m-%d")

            adicionar_lote(
                nome,
                descricao,
                data_iso,
                qtd_comprada,
                qtd_recebida,
                transporte
            )

            st.success("Lote criado com sucesso!")

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

        lote = obter_lote(lote_id)
        qtd_recebida = lote[5]

        total_animais = contar_animais_no_lote(lote_id)

        st.info(f"🐄 Animais cadastrados: {total_animais} / {qtd_recebida}")

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

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Cadastre um lote primeiro")

    else:
        dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

        escolha_lote = st.selectbox("Selecione o lote", list(dict_lotes.keys()))
        lote_id = dict_lotes[escolha_lote]

        animais = listar_animais_por_lote(lote_id)

        if len(animais) == 0:
            st.warning("Nenhum animal neste lote")

        else:
            dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

            escolha_animal = st.selectbox("Selecione o animal", list(dict_animais.keys()))
            animal_id = dict_animais[escolha_animal]

            peso = st.number_input("Peso (kg)", 0.0)

            data = st.date_input("Data")
            hora = st.selectbox("Hora", ["06:00", "08:00", "10:00", "14:00", "16:00", "18:00"])

            # 🔥 ISO CORRETO
            data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
            data_iso = data_hora.strftime("%Y-%m-%d %H:%M")

            if st.button("Salvar Pesagem"):

                if peso <= 0:
                    st.error("Informe um peso válido")

                elif peso > 1000:
                    st.error("Peso muito alto")

                else:
                    adicionar_pesagem(animal_id, peso, data_iso)
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

        animais = listar_animais_por_lote(lote_id)

        gmds = []
        ranking = []

        for animal in animais:
            animal_id = animal[0]
            nome = animal[1]

            pesagens = listar_pesagens(animal_id)

            if len(pesagens) > 1:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])

                # 🔥 SIMPLES AGORA
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                if dias > 0:
                    gmd = (df["Peso"].iloc[-1] - df["Peso"].iloc[0]) / dias

                    if 0 <= gmd <= 2:
                        gmds.append(gmd)
                        ranking.append((nome, gmd))

        if len(gmds) > 0:
            st.write(f"🚀 GMD médio: {sum(gmds)/len(gmds):.3f} kg/dia")

        ranking.sort(key=lambda x: x[1], reverse=True)

        for i, (nome, gmd) in enumerate(ranking, start=1):
            st.write(f"{i}º - {nome}: {gmd:.3f}")

# ---------------------------
# ANÁLISE INDIVIDUAL
# ---------------------------
elif menu == "Analisar Animal":
    st.subheader("Análise do Animal")

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Nenhum lote cadastrado")

    else:
        dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

        escolha_lote = st.selectbox("Lote", list(dict_lotes.keys()))
        lote_id = dict_lotes[escolha_lote]

        animais = listar_animais_por_lote(lote_id)

        dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

        escolha_animal = st.selectbox("Animal", list(dict_animais.keys()))
        animal_id = dict_animais[escolha_animal]

        pesagens = listar_pesagens(animal_id)

        if len(pesagens) > 0:
            df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])

            df["Data"] = pd.to_datetime(df["Data"])
            df = df.sort_values("Data")

            # 🔥 EXIBIÇÃO BR
            df_exibir = df.copy()
            df_exibir["Data"] = df_exibir["Data"].dt.strftime("%d/%m/%Y %H:%M")

            st.dataframe(df_exibir)
            st.line_chart(df.set_index("Data")["Peso"])
