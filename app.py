import streamlit as st
import pandas as pd

try:
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
        listar_pesagens,
        adicionar_ocorrencia,
        listar_ocorrencias
    )
except Exception as e:
    st.error(f"Erro ao importar database: {e}")

if "ocorrencias" not in st.session_state:
    st.session_state.ocorrencias = []
    
def listar_ocorrencias_mem(animal_id):
    return [
        o for o in st.session_state.ocorrencias
        if o["animal_id"] == animal_id
    ]

def salvar_ocorrencia_mem(animal_id, data, tipo, descricao, gravidade):
    st.session_state.ocorrencias.append({
        "animal_id": animal_id,
        "data": str(data),
        "tipo": tipo,
        "descricao": descricao,
        "gravidade": gravidade
    })
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
        "Ocorrências Adversas",
        "Dashboard Sanitário"  # 👈 NOVO
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

#--–--–--—--–-----------------

elif menu == "Dashboard Sanitário":
    st.subheader("🦠 Dashboard Sanitário")

    todas_ocorrencias = []

    for animal in listar_animais():
        oc = listar_ocorrencias(animal[0])
        todas_ocorrencias.extend(oc)

    if len(ocorrencias) == 0:
        st.info("Nenhuma ocorrência registrada")
    else:
        df_oc = pd.DataFrame(ocorrencias)

        # ---------------------------
        # TOTAL DE OCORRÊNCIAS
        # ---------------------------
        total_oc = len(df_oc)
        st.metric("Total de ocorrências", total_oc)

        # ---------------------------
        # TOTAL DE ANIMAIS
        # ---------------------------
        animais = listar_animais()
        total_animais = len(animais)

        if total_animais > 0:
            taxa = (df_oc["animal_id"].nunique() / total_animais) * 100
            st.metric("Taxa de animais com ocorrência (%)", f"{taxa:.2f}%")

        # ---------------------------
        # OCORRÊNCIAS POR TIPO
        # ---------------------------
        st.subheader("📊 Ocorrências por tipo")

        tipos = df_oc["tipo"].value_counts()
        st.bar_chart(tipos)

        # ---------------------------
        # OCORRÊNCIAS POR GRAVIDADE
        # ---------------------------
        st.subheader("🚨 Gravidade")

        gravidade = df_oc["gravidade"].value_counts()
        st.bar_chart(gravidade)

        # ---------------------------
        # OCORRÊNCIAS POR LOTE
        # ---------------------------
        st.subheader("🐄 Ocorrências por lote")

        dados_lote = []

        lotes = listar_lotes()

        for lote in lotes:
            lote_id = lote[0]
            nome_lote = lote[1]

            animais_lote = listar_animais_por_lote(lote_id)
            ids_animais = [a[0] for a in animais_lote]

            oc_lote = df_oc[df_oc["animal_id"].isin(ids_animais)]

            dados_lote.append((nome_lote, len(oc_lote)))

        df_lote = pd.DataFrame(dados_lote, columns=["Lote", "Ocorrências"])
        df_lote = df_lote.set_index("Lote")

        st.bar_chart(df_lote)

        # ---------------------------
        # ALERTAS AUTOMÁTICOS
        # ---------------------------
        st.subheader("🚨 Alertas Sanitários")

        for nome, qtd in dados_lote:
            if qtd >= 5:
                st.error(f"🔴 {nome}: Alta incidência de ocorrências")
            elif qtd >= 2:
                st.warning(f"🟡 {nome}: Atenção moderada")
            else:
                st.success(f"🟢 {nome}: Situação controlada")
        
# ---------------------------
# CORRELAÇÃO GMD x OCORRÊNCIAS
# ---------------------------
        st.subheader("📉 Correlação: GMD x Ocorrências")

        dados_correlacao = []

        animais = listar_animais()

        for animal in animais:
            animal_id = animal[0]
            nome = animal[1]

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

            # contar ocorrências do animal
                    oc = [
                        o for o in st.session_state.ocorrencias
                        if o["animal_id"] == animal_id
                    ]

                    qtd_oc = len(oc)

                    dados_correlacao.append((nome, gmd, qtd_oc))

# ---------------------------
# DATAFRAME
# ---------------------------
        if len(dados_correlacao) > 0:

            df_corr = pd.DataFrame(
                dados_correlacao,
                columns=["Animal", "GMD", "Ocorrencias"]
            )

            st.dataframe(df_corr)

    # ---------------------------
    # GRÁFICO
    # ---------------------------
            st.subheader("📊 Dispersão (GMD x Ocorrências)")

            st.scatter_chart(df_corr, x="Ocorrencias", y="GMD")

    # ---------------------------
    # ANÁLISE AUTOMÁTICA
    # ---------------------------
            st.subheader("🧠 Interpretação")

            media_gmd = df_corr["GMD"].mean()

            for _, row in df_corr.iterrows():

                if row["Ocorrencias"] > 0 and row["GMD"] < media_gmd:
                    st.error(f"🔴 {row['Animal']}: baixo GMD associado a ocorrência")

                elif row["Ocorrencias"] > 0:
                    st.warning(f"🟡 {row['Animal']}: ocorrência sem impacto aparente")

                elif row["GMD"] < media_gmd:
                    st.warning(f"🟠 {row['Animal']}: baixo GMD sem ocorrência registrada")

                else:
                    st.success(f"🟢 {row['Animal']}: bom desempenho e saudável")

        else:
            st.info("Sem dados suficientes para correlação")
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
                gmd_medio = sum(gmds_lote) / len(gmds_lote)
                ranking_lotes.append((nome_lote, gmd_medio))

        ranking_lotes.sort(key=lambda x: x[1], reverse=True)
        # ---------------------------
        # CLASSIFICAÇÃO DOS LOTES
        # ---------------------------
        st.subheader("🧠 Classificação dos Lotes")

        for nome, gmd in ranking_lotes:

            if gmd >= 1.0:
                st.success(f"🟢 {nome}: Excelente desempenho ({gmd:.3f} kg/dia)")

            elif gmd >= 0.7:
                st.info(f"🔵 {nome}: Bom desempenho ({gmd:.3f} kg/dia)")

            elif gmd >= 0.5:
                st.warning(f"🟡 {nome}: Desempenho moderado ({gmd:.3f} kg/dia)")

            else:
                st.error(f"🔴 {nome}: Baixo desempenho ({gmd:.3f} kg/dia)")
        # ---------------------------
        # INTERPRETAÇÃO AUTOMÁTICA
        # ---------------------------
        if len(ranking_lotes) > 1:

            melhor = ranking_lotes[0]
            pior = ranking_lotes[-1]

            diferenca = melhor[1] - pior[1]

            st.subheader("📊 Análise Comparativa")

            st.write(f"📈 Diferença entre melhor e pior lote: {diferenca:.3f} kg/dia")

            if diferenca > 0.5:
                st.error("🚨 Alta variabilidade entre lotes → possível problema de manejo")

            elif diferenca > 0.2:
                st.warning("⚠️ Diferença moderada entre lotes")

            else:
                st.success("✅ Lotes com desempenho homogêneo")
        # ---------------------------
        # RECOMENDAÇÕES AUTOMÁTICAS
        # ---------------------------
        st.subheader("🧾 Recomendações de Manejo")

        for nome, gmd in ranking_lotes:

            if gmd < 0.5:
                st.error(f"🔴 {nome}: Avaliar sanidade, nutrição e manejo URGENTE")

            elif gmd < 0.7:
                st.warning(f"🟡 {nome}: Ajustar dieta e monitorar ganho")

            else:
                st.success(f"🟢 {nome}: Manter manejo atual")
        # ---------------------------
        # SCORE DE EFICIÊNCIA DO LOTE
        # ---------------------------
        ranking_score = []

        for lote_item in todos_lotes:
            lote_id_temp = lote_item[0]
            nome_lote = lote_item[1]

            animais_lote = listar_animais_por_lote(lote_id_temp)

            gmds = []
            ganho_total = 0
            dias_total = 0

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
                        ganho = peso_final - peso_inicial

                        if ganho > 0:
                            gmd = ganho / dias
                            gmds.append(gmd)

                            ganho_total += ganho
                            dias_total += dias

            if len(gmds) > 0 and ganho_total > 0:
                gmd_medio = sum(gmds) / len(gmds)

                custo_total = custo_diario * dias_total
                custo_por_kg = custo_total / ganho_total

                score = gmd_medio / custo_por_kg

                ranking_score.append((nome_lote, score, gmd_medio, custo_por_kg))

        ranking_score.sort(key=lambda x: x[1], reverse=True)
        # ---------------------------
        # EXIBIÇÃO DO SCORE
        # ---------------------------
        if len(ranking_score) > 0:

            st.subheader("🏆 Ranking Final de Eficiência")

            for i, (nome, score, gmd, custo) in enumerate(ranking_score, start=1):
                st.write(
                    f"{i}º - {nome} → Score: {score:.4f} | "
                    f"GMD: {gmd:.3f} | Custo/kg: R$ {custo:.2f}"
                )

            melhor = ranking_score[0]
            pior = ranking_score[-1]

            st.success(f"🥇 Melhor lote: {melhor[0]} (Score {melhor[1]:.4f})")
            st.error(f"🔴 Pior lote: {pior[0]} (Score {pior[1]:.4f})")

        else:
            st.info("Sem dados suficientes para cálculo do score")
        # ---------------------------
        # EXIBIÇÃO + GRÁFICO
        # ---------------------------
        if len(ranking_lotes) > 0:

            st.subheader("📊 Ranking de GMD entre Lotes")

            for i, (nome, gmd) in enumerate(ranking_lotes, start=1):
                st.write(f"{i}º - {nome} → {gmd:.3f} kg/dia")

            df_lotes = pd.DataFrame(ranking_lotes, columns=["Lote", "GMD"])
            df_lotes = df_lotes.set_index("Lote")

            st.bar_chart(df_lotes)

        else:
            st.info("Sem dados suficientes para comparação entre lotes")
# ---------------------------
# ANÁLISE INDIVIDUAL DO ANIMAL
# ---------------------------
elif menu == "Analisar Animal":
    st.subheader("🐄 Análise do Animal")

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

            # ---------------------------
            # DADOS DE PESAGEM
            # ---------------------------
            if len(pesagens) > 0:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                st.subheader("📊 Histórico de Peso")
                st.dataframe(df)
                st.line_chart(df.set_index("Data")["Peso"])

                # ---------------------------
                # CÁLCULO GMD
                # ---------------------------
                if len(df) > 1:
                    peso_inicial = df["Peso"].iloc[0]
                    peso_final = df["Peso"].iloc[-1]

                    dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                    if dias > 0:
                        gmd = (peso_final - peso_inicial) / dias

                        st.subheader("🚀 Desempenho")

                        st.write(f"⚖️ Ganho total: {peso_final - peso_inicial:.2f} kg")
                        st.write(f"📆 Período: {dias} dias")
                        st.write(f"📈 GMD: {gmd:.3f} kg/dia")

                        # ---------------------------
                        # ALERTAS ZOOTÉCNICOS
                        # ---------------------------
                        if gmd < 0:
                            st.error("🚨 Perda de peso — possível doença")
                        elif gmd > 2:
                            st.error("🚨 GMD irreal — revisar dados")
                        elif gmd < 0.5:
                            st.warning("⚠️ GMD baixo")
                        else:
                            st.success("✅ Bom desempenho")

                    else:
                        st.info("Intervalo de datas insuficiente")
            else:
                st.info("Sem pesagens registradas")

            # ---------------------------
            # OCORRÊNCIAS DO ANIMAL
            # ---------------------------
            ocorrencias = listar_ocorrencias_mem(animal_id)

            st.subheader("🚨 Ocorrências do Animal")

            if len(ocorrencias) > 0:
                df_oc = pd.DataFrame(ocorrencias)
                df_oc["data"] = pd.to_datetime(df_oc["data"])

                st.dataframe(df_oc)

                for _, row in df_oc.iterrows():
                    if row["gravidade"] == "Alta":
                        st.error(f"🔴 {row['tipo']} - {row['descricao']}")
                    elif row["gravidade"] == "Média":
                        st.warning(f"🟡 {row['tipo']} - {row['descricao']}")
                    else:
                        st.info(f"🔵 {row['tipo']} - {row['descricao']}")
            else:
                st.success("✅ Nenhuma ocorrência registrada")

            # ---------------------------
            # ALERTA INTELIGENTE (GMD + OCORRÊNCIA)
            # ---------------------------
            if len(pesagens) > 1:
                if 'gmd' in locals():
                    if gmd < 0.5 and len(ocorrencias) > 0:
                        st.error("🚨 Alto risco: baixo desempenho + ocorrência")
                    elif gmd < 0.5:
                        st.warning("⚠️ Baixo desempenho")
                    elif len(ocorrencias) > 0:
                        st.warning("⚠️ Histórico clínico — monitorar")
                    else:
                        st.success("✅ Animal saudável e produtivo")

# ocorrencia adversa
elif menu == "Ocorrências Adversas":
    st.subheader("🚨 Registrar Ocorrência")

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

            escolha = st.selectbox("Selecione o animal", list(dict_animais.keys()))
            animal_id = dict_animais[escolha]
                  

        with st.form("form_ocorrencia"):
            data = st.date_input("Data")
            tipo = st.selectbox("Tipo", ["Doença", "Lesão", "Medicamento", "Outros"])
            descricao = st.text_area("Descrição")
            gravidade = st.selectbox("Gravidade", ["Baixa", "Média", "Alta"])

            custo = st.number_input("💰 Custo do tratamento (R$)", 0.0)
            dias = st.number_input("⏱️ Dias de recuperação", 0)
            status = st.selectbox("Status", ["Em tratamento", "Resolvido"])

            submitted = st.form_submit_button("Salvar Ocorrência")

            if submitted:
                adicionar_ocorrencia(
                    animal_id,
                    str(data),
                    tipo,
                    descricao,
                    gravidade,
                    custo,
                    dias,
                    status
                )

                st.success("Ocorrência registrada no banco!")
