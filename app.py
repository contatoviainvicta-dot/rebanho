import streamlit as st
import pandas as pd
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
            adicionar_lote(
                nome,
                descricao,
                str(data),
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

            if st.button("Salvar Pesagem"):
                if peso <= 0:
                    st.error("Informe um peso válido")
                elif peso > 1000:
                    st.error("Peso muito alto")
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
        animais = listar_animais_por_lote(lote_id)

        st.write(f"🐄 Total: {len(animais)}")

        # ---------------------------
        # PARÂMETROS DE CUSTO
        # ---------------------------
        st.subheader("💰 Parâmetros de Custo")
        custo_diario = st.number_input("Custo diário por animal (R$)", 0.0, 100.0, 10.0)

        # ---------------------------
        # PERÍODO DO LOTE
        # ---------------------------
        datas = []
        for animal in animais:
            pesagens = listar_pesagens(animal[0])
            for p in pesagens:
                datas.append(p[3])

        if len(datas) > 1:
            datas = pd.to_datetime(datas)
            dias_lote = (max(datas) - min(datas)).days
        else:
            dias_lote = 0

        numero_animais = len(animais)
        custo_operacional = custo_diario * numero_animais * dias_lote

        st.write(f"📆 Duração do lote: {dias_lote} dias")
        st.write(f"💰 Custo operacional: R$ {custo_operacional:.2f}")

        # ---------------------------
        # GANHO TOTAL
        # ---------------------------
        ganho_total = 0

        for animal in animais:
            pesagens = listar_pesagens(animal[0])

            if len(pesagens) > 1:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                ganho = df["Peso"].iloc[-1] - df["Peso"].iloc[0]

                if ganho > 0:
                    ganho_total += ganho

        # ---------------------------
        # EFICIÊNCIA ECONÔMICA
        # ---------------------------
        if ganho_total > 0:
            custo_kg = custo_operacional / ganho_total

            st.subheader("💰 Eficiência Econômica")
            st.write(f"⚖️ Ganho total: {ganho_total:.2f} kg")
            st.write(f"💸 Custo por kg: R$ {custo_kg:.2f}")
        else:
            st.info("Sem ganho suficiente para cálculo")

        # ---------------------------
        # RANKING ECONÔMICO
        # ---------------------------
        ranking_economico = []

        for animal in animais:
            animal_id = animal[0]
            nome_animal = animal[1]

            pesagens = listar_pesagens(animal_id)

            if len(pesagens) > 1:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                peso_inicial = df["Peso"].iloc[0]
                peso_final = df["Peso"].iloc[-1]

                dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                if dias > 0:
                    ganho = peso_final - peso_inicial

                    if ganho > 0:
                        custo_animal = custo_diario * dias
                        custo_por_kg = custo_animal / ganho

                        ranking_economico.append((nome_animal, custo_por_kg))

        ranking_economico.sort(key=lambda x: x[1])
        # ---------------------------
        # GRÁFICO GMD ENTRE LOTES
        # ---------------------------
        if len(ranking_lotes) > 0:

            df_lotes = pd.DataFrame(ranking_lotes, columns=["Lote", "GMD"])
            df_lotes = df_lotes.set_index("Lote")

            st.subheader("📊 Comparação de GMD entre Lotes")
            st.bar_chart(df_lotes)
        # ---------------------------
        # EXIBIÇÃO
        # ---------------------------
        if len(ranking_economico) > 0:

            st.subheader("💰 Ranking Econômico (R$/kg)")

            for i, (nome, custo) in enumerate(ranking_economico, start=1):
                st.write(f"{i}º - {nome} → R$ {custo:.2f}/kg")

            melhor = ranking_economico[0]
            pior = ranking_economico[-1]

            st.success(f"🥇 Mais eficiente: {melhor[0]} (R$ {melhor[1]:.2f}/kg)")
            st.warning(f"⚠️ Menos eficiente: {pior[0]} (R$ {pior[1]:.2f}/kg)")

            # ALERTAS
            st.subheader("🚨 Alertas Econômicos")

            for nome, custo in ranking_economico:
                if custo > 15:
                    st.error(f"🔴 {nome} com custo muito alto (R$ {custo:.2f}/kg)")
                elif custo > 10:
                    st.warning(f"🟡 {nome} com custo moderado (R$ {custo:.2f}/kg)")

        else:
            st.info("Sem dados suficientes para ranking econômico")

        # ---------------------------
        # GMD MÉDIO DO LOTE
        # ---------------------------
        gmds = []

        for animal in animais:
            pesagens = listar_pesagens(animal[0])

            if len(pesagens) > 1:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                peso_inicial = df["Peso"].iloc[0]
                peso_final = df["Peso"].iloc[-1]

                dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                if dias > 0:
                    gmd = (peso_final - peso_inicial) / dias

                    if 0 <= gmd <= 2:
                        gmds.append(gmd)

        # ---------------------------
        # EXIBIÇÃO DO GMD
        # ---------------------------
        if len(gmds) > 0:
            gmd_medio = sum(gmds) / len(gmds)

            st.subheader("📈 Desempenho Zootécnico")
            st.write(f"🚀 GMD médio do lote: {gmd_medio:.3f} kg/dia")

            if gmd_medio < 0.5:
                st.warning("⚠️ Lote com baixo desempenho")
            else:
                st.success("✅ Bom desempenho")

        else:
            st.info("Sem dados suficientes para GMD do lote")
                # ---------------------------
        # RANKING DE GMD POR ANIMAL
        # ---------------------------
        ranking_gmd = []

        for animal in animais:
            animal_id = animal[0]
            nome_animal = animal[1]

            pesagens = listar_pesagens(animal_id)

            if len(pesagens) > 1:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                peso_inicial = df["Peso"].iloc[0]
                peso_final = df["Peso"].iloc[-1]

                dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                if dias > 0:
                    gmd = (peso_final - peso_inicial) / dias

                    if 0 <= gmd <= 2:
                        ranking_gmd.append((nome_animal, gmd))

        ranking_gmd.sort(key=lambda x: x[1], reverse=True)

        # ---------------------------
        # EXIBIÇÃO
        # ---------------------------
        if len(ranking_gmd) > 0:

            st.subheader("🏆 Ranking de GMD (Animal)")

            for i, (nome, gmd) in enumerate(ranking_gmd, start=1):
                st.write(f"{i}º - {nome} → {gmd:.3f} kg/dia")

            melhor = ranking_gmd[0]
            pior = ranking_gmd[-1]

            st.success(f"🥇 Melhor: {melhor[0]} ({melhor[1]:.3f} kg/dia)")
            st.warning(f"⚠️ Pior: {pior[0]} ({pior[1]:.3f} kg/dia)")

        else:
            st.info("Sem dados suficientes para ranking de GMD")
         # ---------------------------
        # RANKING DE GMD ENTRE LOTES
        # ---------------------------
        ranking_lotes = []

        todos_lotes = listar_lotes()

        for lote_item in todos_lotes:
            lote_id_temp = lote_item[0]
            nome_lote = lote_item[1]

            animais_lote = listar_animais_por_lote(lote_id_temp)

            gmds_lote = []

            for animal in animais_lote:
                pesagens = listar_pesagens(animal[0])

                if len(pesagens) > 1:
                    df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                    df["Data"] = pd.to_datetime(df["Data"])
                    df = df.sort_values("Data")

                    peso_inicial = df["Peso"].iloc[0]
                    peso_final = df["Peso"].iloc[-1]

                    dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                    if dias > 0:
                        gmd = (peso_final - peso_inicial) / dias

                        if 0 <= gmd <= 2:
                            gmds_lote.append(gmd)

            if len(gmds_lote) > 0:
                gmd_medio_lote = sum(gmds_lote) / len(gmds_lote)
                ranking_lotes.append((nome_lote, gmd_medio_lote))

        ranking_lotes.sort(key=lambda x: x[1], reverse=True)

        # ---------------------------
        # EXIBIÇÃO
        # ---------------------------
        if len(ranking_lotes) > 0:

            st.subheader("📊 Ranking de GMD entre Lotes")

            for i, (nome, gmd) in enumerate(ranking_lotes, start=1):
                st.write(f"{i}º - {nome} → {gmd:.3f} kg/dia")

            melhor = ranking_lotes[0]
            pior = ranking_lotes[-1]

            st.success(f"🥇 Melhor lote: {melhor[0]} ({melhor[1]:.3f})")
            st.warning(f"⚠️ Pior lote: {pior[0]} ({pior[1]:.3f})")

        else:
            st.info("Sem dados suficientes para comparação entre lotes")         
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

        escolha_lote = st.selectbox("Selecione o lote", list(dict_lotes.keys()))
        lote_id = dict_lotes[escolha_lote]

        animais = listar_animais_por_lote(lote_id)

        if len(animais) == 0:
            st.warning("Nenhum animal neste lote")

        else:
            dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

            escolha_animal = st.selectbox("Selecione o animal", list(dict_animais.keys()))
            animal_id = dict_animais[escolha_animal]

            pesagens = listar_pesagens(animal_id)

            if len(pesagens) > 0:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                st.dataframe(df)
                st.line_chart(df.set_index("Data")["Peso"])
