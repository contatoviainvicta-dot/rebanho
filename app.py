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
        "Analisar Animal",
        "Comparar Lotes"
    ]
)

# ---------------------------
# CADASTRAR LOTE
# ----------------------
if menu == "Cadastrar Lote":
    st.subheader("Novo Lote")

    nome = st.text_input("Nome do lote")
    descricao = st.text_area("Descrição")
    data = st.date_input("Data")

    qtd_comprada = st.number_input("Quantidade comprada", 0)
    qtd_recebida = st.number_input("Quantidade recebida", 0)
    transporte = st.text_input("Tipo de transporte")

    # ---------------------------
    # PRIORIDADE 1
    # ---------------------------
    preco_por_animal = st.number_input("Preço por animal (R$)", 0.0)

    raca = st.selectbox(
        "Raça",
        ["Nelore", "Angus", "Cruzamento", "Outros"]
    )

    categoria = st.selectbox(
        "Categoria",
        ["Bezerro", "Recria", "Engorda"]
    )

    # ---------------------------
    # PRIORIDADE 2
    # ---------------------------
    mortalidade = st.number_input("Mortalidade no lote", 0)

    tipo_alimentacao = st.selectbox(
        "Tipo de alimentação",
        ["Pasto", "Confinamento", "Semi-confinamento"]
    )

    tipo_dieta = st.selectbox(
        "Tipo de dieta",
        ["Capim", "Ração", "Silagem", "Misto"]
    )

    # ---------------------------
    # CÁLCULO
    # ---------------------------
    custo_total = preco_por_animal * qtd_comprada
    st.info(f"💰 Custo total estimado: R$ {custo_total:.2f}")

    # ---------------------------
    # BOTÃO
    # ---------------------------
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

            # RESUMO
            st.write("### 📊 Resumo do Lote")
            st.write(f"🐄 Raça: {raca}")
            st.write(f"📦 Categoria: {categoria}")
            st.write(f"💰 Custo total: R$ {custo_total:.2f}")
            st.write(f"💀 Mortalidade: {mortalidade}")
            st.write(f"🌾 Alimentação: {tipo_alimentacao}")
            st.write(f"🥣 Dieta: {tipo_dieta}")
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
# ----

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

        st.write(f"📦 Comprados: {lote[4]}")
        st.write(f"📥 Recebidos: {lote[5]}")

        animais = listar_animais_por_lote(lote_id)

        st.write(f"🐄 Total: {len(animais)}")

        # ---------------------------
        # GMD MÉDIO DO LOTE
        # ---------------------------
        gmds = []

        for animal in animais:
            animal_id = animal[0]
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
                        gmds.append(gmd)

        # RESULTADO
        if len(gmds) > 0:
            gmd_medio = sum(gmds) / len(gmds)

            st.subheader("📊 Desempenho do Lote")
            st.write(f"🐄 Animais analisados: {len(gmds)}")
            st.write(f"🚀 GMD médio: {gmd_medio:.3f} kg/dia")

            if gmd_medio < 0.5:
                st.warning("⚠️ Lote com baixo desempenho")
            else:
                st.success("✅ Lote com bom desempenho")

        else:
            st.info("Dados insuficientes para cálculo do GMD do lote")

        # ---------------------------
        # RANKING + GRÁFICO + ALERTAS
        # ---------------------------
        ranking = []

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
                        ranking.append((nome_animal, gmd))

        ranking.sort(key=lambda x: x[1], reverse=True)

        if len(ranking) > 0:

            # GRÁFICO
            st.subheader("📊 Comparação de GMD por Animal")

            df_grafico = pd.DataFrame(ranking, columns=["Animal", "GMD"])
            df_grafico = df_grafico.set_index("Animal")

            st.bar_chart(df_grafico)

            # RANKING
            st.subheader("🏆 Ranking de Desempenho")

            for i, (nome, gmd) in enumerate(ranking, start=1):
                st.write(f"{i}º - {nome} → {gmd:.3f} kg/dia")

            melhor = ranking[0]
            pior = ranking[-1]

            st.success(f"🥇 Melhor: {melhor[0]} ({melhor[1]:.3f} kg/dia)")
            st.warning(f"⚠️ Pior: {pior[0]} ({pior[1]:.3f} kg/dia)")

            # ALERTAS
            st.subheader("🚨 Alertas do Lote")

            for nome, gmd in ranking:
                if gmd < 0.5:
                    st.error(f"🔴 {nome} com baixo desempenho ({gmd:.3f})")
                elif gmd < 0.7:
                    st.warning(f"🟡 {nome} em atenção ({gmd:.3f})")

        else:
            st.info("Sem dados suficientes para ranking")


        
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

                # ---------------------------
                # CÁLCULO + VALIDAÇÃO GMD
                # ---------------------------
                if len(df) > 1:

                    peso_inicial = df["Peso"].iloc[0]
                    peso_final = df["Peso"].iloc[-1]

                    data_inicial = df["Data"].iloc[0]
                    data_final = df["Data"].iloc[-1]

                    dias = (data_final - data_inicial).days

                    if dias > 0:
                        gmd = (peso_final - peso_inicial) / dias

                        st.subheader("📊 Desempenho")

                        st.write(f"⚖️ Ganho total: {peso_final - peso_inicial:.2f} kg")
                        st.write(f"📆 Período: {dias} dias")
                        st.write(f"🚀 GMD: {gmd:.3f} kg/dia")

                        # ✅ VALIDAÇÃO
                        if gmd < 0:
                            st.error("🚨 Perda de peso detectada — possível doença ou manejo inadequado")

                        elif gmd > 2:
                            st.error("🚨 GMD irreal — verificar dados (peso ou datas incorretas)")

                        elif gmd < 0.5:
                            st.warning("⚠️ GMD baixo — possível problema nutricional ou sanitário")

                        else:
                            st.success("✅ GMD adequado")

                    else:
                        st.info("Intervalo de datas insuficiente para cálculo")

            else:
                st.info("Sem pesagens registradas")

# ---------------------------
# COMPARAÇÃO ENTRE LOTES
# ---------------------------
elif menu == "Comparar Lotes":
    st.subheader("📊 Comparação entre Lotes")

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Nenhum lote cadastrado")

    else:
        dados_lotes = []

        for lote in lotes:
            lote_id = lote[0]
            nome_lote = lote[1]

            animais = listar_animais_por_lote(lote_id)

            gmds = []

            for animal in animais:
                animal_id = animal[0]
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
                            gmds.append(gmd)

            if len(gmds) > 0:
                gmd_medio = sum(gmds) / len(gmds)
                dados_lotes.append((nome_lote, gmd_medio))

        # ---------------------------
        # RESULTADO
        # ---------------------------
        if len(dados_lotes) > 0:

            df_lotes = pd.DataFrame(dados_lotes, columns=["Lote", "GMD"])
            df_lotes = df_lotes.set_index("Lote")

            # 📊 GRÁFICO
            st.subheader("📊 GMD médio por lote")
            st.bar_chart(df_lotes)

            # 🏆 INTERPRETAÇÃO
            melhor = df_lotes["GMD"].idxmax()
            pior = df_lotes["GMD"].idxmin()

            st.success(f"🥇 Melhor lote: {melhor}")
            st.warning(f"⚠️ Pior lote: {pior}")

            # 🚨 ALERTAS
            st.subheader("🚨 Alertas")

            for lote, gmd in dados_lotes:
                if gmd < 0.5:
                    st.error(f"🔴 {lote} com baixo desempenho ({gmd:.3f})")
                elif gmd < 0.7:
                    st.warning(f"🟡 {lote} em atenção ({gmd:.3f})")

        else:
            st.info("Sem dados suficientes para comparação entre lotes")
