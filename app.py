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
        "Dashboard Executivo",
        "Cadastrar Lote",
        "Cadastrar Animal",
        "Registrar Pesagem",
        "Analisar por Lote",
        "Analisar Animal",
        "Ocorrências Adversas",
        "Dashboard Sanitário",
        "Painel de Decisão",
        "Pesquisar Ocorrências"
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

    # ---------------------------
    # SELEÇÃO DE LOTE
    # ---------------------------
    lotes = listar_lotes()

    opcoes = ["Todos os lotes"]
    dict_lotes = {}

    for l in lotes:
        nome = f"{l[1]} (ID {l[0]})"
        opcoes.append(nome)
        dict_lotes[nome] = l[0]

    escolha = st.selectbox("Selecione o lote para análise", opcoes)

    # ---------------------------
    # DEFINIR ANIMAIS (FALTAVA ISSO)
    # ---------------------------
    if escolha == "Todos os lotes":
        animais = listar_animais()
    else:
        lote_id = dict_lotes[escolha]
        animais = listar_animais_por_lote(lote_id)

    # ---------------------------
    # COLETAR OCORRÊNCIAS
    # ---------------------------
    todas_ocorrencias = []

    for animal in animais:
        oc = listar_ocorrencias(animal[0])
        todas_ocorrencias.extend(oc)

    # ---------------------------
    # DATAFRAME
    # ---------------------------
    df_oc = pd.DataFrame(
        todas_ocorrencias,
        columns=[
            "id", "animal_id", "data", "tipo",
            "descricao", "gravidade",
            "custo", "dias_recuperacao", "status"
        ]
    )

    # ---------------------------
    # MÉTRICAS
    # ---------------------------
    total_animais = len(animais)

    if total_animais > 0 and len(df_oc) > 0:
        animais_com_oc = df_oc["animal_id"].nunique()
        incidencia = (animais_com_oc / total_animais) * 100
    else:
        incidencia = 0

    st.metric("📊 Incidência (%)", f"{incidencia:.2f}%")

    # ---------------------------
    # OCORRÊNCIAS POR TIPO
    # ---------------------------
    if len(df_oc) > 0:
        st.subheader("📊 Ocorrências por tipo")
        st.bar_chart(df_oc["tipo"].value_counts())

        st.subheader("🚨 Gravidade")
        st.bar_chart(df_oc["gravidade"].value_counts())

    # ---------------------------
    # INCIDÊNCIA POR LOTE
    # ---------------------------
    st.subheader("🐄 Incidência por lote (%)")

    dados_lote = []

    for lote in lotes:
        lote_id = lote[0]
        nome_lote = lote[1]

        animais_lote = listar_animais_por_lote(lote_id)
        total = len(animais_lote)

        ids_animais = [a[0] for a in animais_lote]
        oc_lote = df_oc[df_oc["animal_id"].isin(ids_animais)]

        doentes = oc_lote["animal_id"].nunique()

        incidencia_lote = (doentes / total) * 100 if total > 0 else 0

        dados_lote.append((nome_lote, incidencia_lote))

    df_lote = pd.DataFrame(dados_lote, columns=["Lote", "Incidência (%)"]).set_index("Lote")
    st.bar_chart(df_lote)

    # ---------------------------
    # INCIDÊNCIA POR TIPO
    # ---------------------------
    st.subheader("🦠 Incidência por tipo (%)")

    dados_tipo = []

    if total_animais > 0 and len(df_oc) > 0:
        for tipo in df_oc["tipo"].unique():
            df_tipo = df_oc[df_oc["tipo"] == tipo]
            doentes = df_tipo["animal_id"].nunique()
            incidencia_tipo = (doentes / total_animais) * 100
            dados_tipo.append((tipo, incidencia_tipo))

        df_tipo = pd.DataFrame(dados_tipo, columns=["Tipo", "Incidência (%)"]).set_index("Tipo")
        st.bar_chart(df_tipo)
# ---------------------------
# CURVA EPIDÊMICA
# ---------------------------
    st.subheader("📈 Curva Epidêmica")

    if len(df_oc) > 0:

        # garantir formato datetime
        df_oc["data"] = pd.to_datetime(df_oc["data"])

        # agrupar por dia
        curva = df_oc.groupby("data").size()

        # ordenar
        curva_tipo = df_oc.groupby(["data", "tipo"]).size().unstack(fill_value=0)
        st.line_chart(curva_tipo)

        # gráfico
        st.line_chart(curva)

    else:
        st.info("Sem dados suficientes para curva epidêmica")
    # ---------------------------
    # ALERTAS
    # ---------------------------
    st.subheader("🚨 Alertas Sanitários")

    for nome, inc in dados_lote:
        if inc > 20:
            st.error(f"🔴 {nome}: alta incidência ({inc:.1f}%)")
        elif inc > 5:
            st.warning(f"🟡 {nome}: incidência moderada ({inc:.1f}%)")
        else:
            st.success(f"🟢 {nome}: controle adequado ({inc:.1f}%)")

    st.subheader("🚨 Alertas por tipo")

    for tipo, inc in dados_tipo:
        if inc > 20:
            st.error(f"🔴 {tipo}: alta incidência ({inc:.1f}%)")
        elif inc > 5:
            st.warning(f"🟡 {tipo}: incidência moderada ({inc:.1f}%)")
        else:
            st.success(f"🟢 {tipo}: controle adequado ({inc:.1f}%)")
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

        st.subheader("🚨 Alertas por tipo")

        for tipo, inc in dados_tipo:
            if inc > 20:
                st.error(f"🔴 {tipo}: alta incidência ({inc:.1f}%)")
            elif inc > 5:
                st.warning(f"🟡 {tipo}: incidência moderada ({inc:.1f}%)")
        else:
            st.success(f"🟢 {tipo}: controle adequado ({inc:.1f}%)")
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
                        
        preco_kg = st.number_input("Preço do kg (R$)", 0.0, 50.0, 10.0)

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

        receita = ganho_total * preco_kg

        custo_sanitario = 0

        for animal in animais:
            ocorrencias = listar_ocorrencias(animal[0])
    
            for oc in ocorrencias:
                if oc[6] is not None:  # coluna custo
                    custo_sanitario += oc[6]

        lucro = receita - (custo_operacional + custo_sanitario)
        
        st.subheader("💰 Resultado Econômico")

        st.write(f"📈 Receita estimada: R$ {receita:.2f}")
        st.write(f"💸 Custo operacional: R$ {custo_operacional:.2f}")
        st.write(f"💊 Custo sanitário: R$ {custo_sanitario:.2f}")

        if lucro > 0:
            st.success(f"🟢 Lucro: R$ {lucro:.2f}")
        else:
            st.error(f"🔴 Prejuízo: R$ {lucro:.2f}")

        lucro_por_animal = lucro / len(animais) if len(animais) > 0 else 0
        st.metric("💰 Lucro por animal", f"R$ {lucro_por_animal:.2f}")
        st.metric("💊 Custo sanitário total", f"R$ {custo_sanitario:.2f}")
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
            ocorrencias = listar_ocorrencias(animal_id)

            st.subheader("🚨 Ocorrências do Animal")

            if len(ocorrencias) > 0:

                df_oc = pd.DataFrame(
                    ocorrencias,
                    columns=[
                        "id",
                        "animal_id",
                        "data",
                        "tipo",
                        "descricao",
                        "gravidade",
                        "custo",
                        "dias_recuperacao",
                        "status"
                    ]
                )

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

# ---------------------------
# OCORRÊNCIAS ADVERSAS
# ---------------------------
elif menu == "Ocorrências Adversas":
    st.subheader("🚨 Registrar Ocorrência")

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Nenhum lote cadastrado")

    else:
        # ---------------------------
        # SELEÇÃO DE LOTE
        # ---------------------------
        dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

        escolha_lote = st.selectbox("Selecione o lote", list(dict_lotes.keys()))
        lote_id = dict_lotes[escolha_lote]

        # ---------------------------
        # SELEÇÃO DE ANIMAL
        # ---------------------------
        animais = listar_animais_por_lote(lote_id)

        if len(animais) == 0:
            st.warning("Nenhum animal neste lote")

        else:
            dict_animais = {f"{a[1]} (ID {a[0]})": a[0] for a in animais}

            escolha_animal = st.selectbox("Selecione o animal", list(dict_animais.keys()))
            animal_id = dict_animais[escolha_animal]

            # ---------------------------
            # FORMULÁRIO
            # ---------------------------
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

                    st.success("Ocorrência registrada com sucesso!")
                    
# ---------------------------
# PAINEL DE DECISÃO
# ---------------------------
elif menu == "Painel de Decisão":
    st.title("📊 Painel de Decisão")

    # ---------------------------
    # PARÂMETROS ECONÔMICOS
    # ---------------------------
    preco_kg = st.number_input("Preço do kg (R$)", 0.0, 50.0, 10.0)
    custo_diario = st.number_input("Custo diário por animal (R$)", 0.0, 100.0, 10.0)

    # ---------------------------
    # MODO DE ANÁLISE
    # ---------------------------
    opcao = st.selectbox(
        "Modo de análise",
        ["Todos os lotes", "Selecionar lote específico"]
    )

    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Nenhum lote cadastrado")
        st.stop()

    dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

    # ---------------------------
    # DEFINIR LOTES PARA ANÁLISE
    # ---------------------------
    if opcao == "Selecionar lote específico":
        escolha = st.selectbox("Escolha o lote", list(dict_lotes.keys()))
        lote_id_escolhido = dict_lotes[escolha]

        st.info(f"📊 Analisando apenas: {escolha}")

        lotes_para_analise = [l for l in lotes if l[0] == lote_id_escolhido]

    else:
        lotes_para_analise = lotes

    # 🔴 ESSENCIAL (ANTES DO LOOP)
    dados_lotes = []

    # ---------------------------
    # PROCESSAMENTO
    # ---------------------------
    for lote in lotes_para_analise:
        lote_id = lote[0]
        nome_lote = lote[1]

        animais = listar_animais_por_lote(lote_id)

        ganho_total = 0
        custo_sanitario = 0
        dias_total = 0

        for animal in animais:
            animal_id = animal[0]

            pesagens = listar_pesagens(animal_id)

            if len(pesagens) > 1:
                df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
                df["Data"] = pd.to_datetime(df["Data"])
                df = df.sort_values("Data")

                ganho = df["Peso"].iloc[-1] - df["Peso"].iloc[0]
                dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

                if ganho > 0 and dias > 0:
                    ganho_total += ganho
                    dias_total += dias

            ocorrencias = listar_ocorrencias(animal_id)

            for oc in ocorrencias:
                if oc[6] is not None:
                    custo_sanitario += oc[6]

        numero_animais = len(animais)

        custo_operacional = custo_diario * numero_animais * dias_total
        receita = ganho_total * preco_kg
        lucro = receita - (custo_operacional + custo_sanitario)

        dados_lotes.append((nome_lote, lucro, receita, custo_operacional, custo_sanitario))

    # ---------------------------
    # DATAFRAME
    # ---------------------------
    df_decisao = pd.DataFrame(
        dados_lotes,
        columns=["Lote", "Lucro", "Receita", "Custo Operacional", "Custo Sanitário"]
    )

    df_decisao = df_decisao.sort_values(by="Lucro", ascending=False)

    st.subheader("📈 Visão Geral")

    if len(df_decisao) > 0:

        total_lucro = df_decisao["Lucro"].sum()
        st.metric("💰 Lucro total", f"R$ {total_lucro:.2f}")

        melhor = df_decisao.iloc[0]
        pior = df_decisao.iloc[-1]

        st.success(f"🥇 Melhor lote: {melhor['Lote']} (R$ {melhor['Lucro']:.2f})")
        st.error(f"🔴 Pior lote: {pior['Lote']} (R$ {pior['Lucro']:.2f})")

    else:
        st.warning("Nenhum lote com dados suficientes")
        st.stop()

    # ---------------------------
    # RANKING
    # ---------------------------
    st.subheader("📊 Ranking de Lotes")
    st.dataframe(df_decisao)

    # ---------------------------
    # GRÁFICO
    # ---------------------------
    st.subheader("📉 Lucro por lote")
    df_plot = df_decisao.set_index("Lote")["Lucro"]
    st.bar_chart(df_plot)

    # ---------------------------
    # ALERTAS
    # ---------------------------
    st.subheader("🚨 Alertas de Decisão")

    for _, row in df_decisao.iterrows():

        if row["Lucro"] < 0:
            st.error(f"🔴 {row['Lote']}: prejuízo → revisar manejo urgente")

        elif row["Custo Sanitário"] > row["Receita"] * 0.2:
            st.warning(f"🟡 {row['Lote']}: custo sanitário elevado")

        else:
            st.success(f"🟢 {row['Lote']}: operação saudável")

# ---------------------------
# PESQUISAR OCORRÊNCIAS
# ---------------------------
elif menu == "Pesquisar Ocorrências":
    st.title("🔎 Pesquisa de Ocorrências")

    lotes = listar_lotes()

    # ---------------------------
    # FILTRO POR LOTE
    # ---------------------------
    dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

    escolha_lote = st.selectbox(
        "Filtrar por lote",
        ["Todos"] + list(dict_lotes.keys())
    )

    # ---------------------------
    # FILTRO POR TIPO
    # ---------------------------
    tipo = st.selectbox(
        "Tipo",
        ["Todos", "Doença", "Lesão", "Medicamento", "Outros"]
    )

    # ---------------------------
    # FILTRO POR GRAVIDADE
    # ---------------------------
    gravidade = st.selectbox(
        "Gravidade",
        ["Todas", "Baixa", "Média", "Alta"]
    )

    # ---------------------------
    # COLETAR OCORRÊNCIAS
    # ---------------------------
    todas_ocorrencias = []

    if escolha_lote == "Todos":
        animais = listar_animais()
    else:
        lote_id = dict_lotes[escolha_lote]
        animais = listar_animais_por_lote(lote_id)

    for animal in animais:
        oc = listar_ocorrencias(animal[0])
        todas_ocorrencias.extend(oc)

    # ---------------------------
    # DATAFRAME
    # ---------------------------
    df_oc = pd.DataFrame(
        todas_ocorrencias,
        columns=[
            "id",
            "animal_id",
            "data",
            "tipo",
            "descricao",
            "gravidade",
            "custo",
            "dias_recuperacao",
            "status"
        ]
    )

    # ---------------------------
    # APLICAR FILTROS
    # ---------------------------
    if len(df_oc) > 0:

        if tipo != "Todos":
            df_oc = df_oc[df_oc["tipo"] == tipo]

        if gravidade != "Todas":
            df_oc = df_oc[df_oc["gravidade"] == gravidade]

        # ordenar por data (opcional, mas recomendado)
        df_oc["data"] = pd.to_datetime(df_oc["data"])
        df_oc = df_oc.sort_values(by="data", ascending=False)

    # ---------------------------
    # EXIBIR RESULTADOS
    # ---------------------------
            # ---------------------------
# EXIBIR RESULTADOS
# ---------------------------
    st.subheader("📊 Resultados")

    if len(df_oc) > 0:
        st.dataframe(df_oc)

    # ---------------------------
    # ANÁLISE DAS OCORRÊNCIAS
    # ---------------------------

    # 1. CUSTO TOTAL
        custo_total = df_oc["custo"].fillna(0).sum()
        st.metric("💰 Custo total", f"R$ {custo_total:.2f}")

    # 2. OCORRÊNCIAS POR TIPO
        st.subheader("📊 Ocorrências por tipo")
        st.bar_chart(df_oc["tipo"].value_counts())

    # 3. ALERTA AUTOMÁTICO
        if len(df_oc) >= 10:
            st.error("🚨 Alta incidência de ocorrências")
        elif len(df_oc) >= 5:
            st.warning("⚠️ Incidência moderada")
        else:
            st.success("✅ Baixa incidência")

    # 4. DOENÇA MAIS CARA
        custo_por_tipo = df_oc.groupby("tipo")["custo"].sum()

        if len(custo_por_tipo) > 0:
            tipo_mais_caro = custo_por_tipo.idxmax()
            valor_mais_caro = custo_por_tipo.max()

            st.warning(
            f"💸 Maior impacto econômico: {tipo_mais_caro} "
            f"(R$ {valor_mais_caro:.2f})"
            )

    else:
        st.info("Nenhuma ocorrência encontrada com esses filtros")

# ---------------------------
# ALERTAS AUTOMÁTICOS INTELIGENTES
# ---------------------------
st.subheader("🧠 Alertas Inteligentes")

for lote in listar_lotes():

    lote_id = lote[0]
    nome_lote = lote[1]

    animais = listar_animais_por_lote(lote_id)
    total_animais = len(animais)

    if total_animais == 0:
        continue

    todas_ocorrencias = []
    gmds = []
    custo_total = 0

    for animal in animais:
        animal_id = animal[0]

        # OCORRÊNCIAS
        oc = listar_ocorrencias(animal_id)
        todas_ocorrencias.extend(oc)

        for o in oc:
            if o[6] is not None:
                custo_total += o[6]

        # GMD
        pesagens = listar_pesagens(animal_id)

        if len(pesagens) > 1:
            df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
            df["Data"] = pd.to_datetime(df["Data"])
            df = df.sort_values("Data")

            ganho = df["Peso"].iloc[-1] - df["Peso"].iloc[0]
            dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

            if dias > 0:
                gmd = ganho / dias
                if 0 <= gmd <= 2:
                    gmds.append(gmd)

    # ---------------------------
    # CÁLCULOS
    # ---------------------------
    incidencia = 0
    if len(todas_ocorrencias) > 0:
        animais_doentes = len(set([o[1] for o in todas_ocorrencias]))
        incidencia = (animais_doentes / total_animais) * 100

    gmd_medio = sum(gmds) / len(gmds) if len(gmds) > 0 else 0

    # ---------------------------
    # ALERTAS
    # ---------------------------

    # 🔴 CRÍTICO
    if incidencia > 20 and gmd_medio < 0.5:
        st.error(
            f"🔴 {nome_lote}: Alta incidência ({incidencia:.1f}%) + baixo GMD ({gmd_medio:.2f}) → possível problema sanitário grave"
        )

    # 🟡 ECONÔMICO
    elif custo_total > 1000:
        st.warning(
            f"🟡 {nome_lote}: Custo sanitário elevado (R$ {custo_total:.2f})"
        )

    # 🟠 SURTO (tendência temporal simples)
    elif len(todas_ocorrencias) >= 5:
        st.warning(
            f"🟠 {nome_lote}: Aumento de ocorrências → monitorar possível surto"
        )

    # 🟢 SAUDÁVEL
    else:
        st.success(
            f"🟢 {nome_lote}: Situação controlada (Incidência {incidencia:.1f}%, GMD {gmd_medio:.2f})"
        )

    elif menu == "Dashboard Executivo":
    st.title("📊 Dashboard Executivo")

    # ---------------------------
    # PARÂMETROS
    # ---------------------------
    preco_kg = st.number_input("Preço do kg (R$)", 0.0, 50.0, 10.0)
    custo_diario = st.number_input("Custo diário por animal (R$)", 0.0, 100.0, 10.0)

    # ---------------------------
    # SELEÇÃO DE LOTE
    # ---------------------------
    lotes = listar_lotes()

    if len(lotes) == 0:
        st.warning("Nenhum lote cadastrado")
        st.stop()

    dict_lotes = {f"{l[1]} (ID {l[0]})": l[0] for l in lotes}

    escolha = st.selectbox("Selecione o lote", list(dict_lotes.keys()))
    lote_id = dict_lotes[escolha]

    animais = listar_animais_por_lote(lote_id)

    if len(animais) == 0:
        st.warning("Nenhum animal no lote")
        st.stop()

    # ---------------------------
    # CÁLCULOS
    # ---------------------------
    ganho_total = 0
    custo_sanitario = 0
    dias_total = 0
    animais_com_oc = set()
    gmds = []

    for animal in animais:
        animal_id = animal[0]

        # PESAGENS
        pesagens = listar_pesagens(animal_id)

        if len(pesagens) > 1:
            df = pd.DataFrame(pesagens, columns=["ID", "Animal", "Peso", "Data"])
            df["Data"] = pd.to_datetime(df["Data"])
            df = df.sort_values("Data")

            ganho = df["Peso"].iloc[-1] - df["Peso"].iloc[0]
            dias = (df["Data"].iloc[-1] - df["Data"].iloc[0]).days

            if ganho > 0 and dias > 0:
                ganho_total += ganho
                dias_total += dias

                gmd = ganho / dias
                if 0 <= gmd <= 2:
                    gmds.append(gmd)

        # OCORRÊNCIAS
        ocorrencias = listar_ocorrencias(animal_id)

        if len(ocorrencias) > 0:
            animais_com_oc.add(animal_id)

        for oc in ocorrencias:
            if oc[6] is not None:
                custo_sanitario += oc[6]

    numero_animais = len(animais)

    custo_operacional = custo_diario * numero_animais * dias_total
    receita = ganho_total * preco_kg
    lucro = receita - (custo_operacional + custo_sanitario)

    # ---------------------------
    # MÉTRICAS
    # ---------------------------
    incidencia = (len(animais_com_oc) / numero_animais) * 100 if numero_animais > 0 else 0
    gmd_medio = sum(gmds) / len(gmds) if len(gmds) > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Lucro", f"R$ {lucro:.2f}")
    col2.metric("🦠 Incidência", f"{incidencia:.2f}%")
    col3.metric("📈 GMD", f"{gmd_medio:.3f} kg/dia")

    # ---------------------------
    # STATUS INTELIGENTE
    # ---------------------------
    st.subheader("🚨 Status do Lote")

    if lucro < 0:
        st.error("🔴 Prejuízo → ação imediata necessária")

    elif incidencia > 20:
        st.error("🔴 Alta incidência sanitária")

    elif gmd_medio < 0.5:
        st.warning("🟡 Baixo desempenho produtivo")

    elif custo_sanitario > receita * 0.2:
        st.warning("🟡 Custo sanitário elevado")

    else:
        st.success("🟢 Lote saudável e lucrativo")

    # ---------------------------
    # RESUMO RÁPIDO
    # ---------------------------
    st.subheader("📋 Resumo")

    st.write(f"🐄 Animais: {numero_animais}")
    st.write(f"⚖️ Ganho total: {ganho_total:.2f} kg")
    st.write(f"💸 Custo sanitário: R$ {custo_sanitario:.2f}")
