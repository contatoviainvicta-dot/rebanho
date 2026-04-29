import sqlite3

def conectar():
    return sqlite3.connect("data.db", check_same_thread=False)
import sqlite3

def criar_tabelas():
    conn = sqlite3.connect("rebanho.db")
    cursor = conn.cursor()

    # cria tabela básica (antiga)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ocorrencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER,
        data TEXT,
        tipo TEXT,
        descricao TEXT,
        gravidade TEXT
    )
    """)

    # -------- MIGRAÇÃO SEGURA --------
    cursor.execute("PRAGMA table_info(ocorrencias)")
    colunas = [c[1] for c in cursor.fetchall()]

    if "custo" not in colunas:
        cursor.execute("ALTER TABLE ocorrencias ADD COLUMN custo REAL")

    if "dias_recuperacao" not in colunas:
        cursor.execute("ALTER TABLE ocorrencias ADD COLUMN dias_recuperacao INTEGER")

    if "status" not in colunas:
        cursor.execute("ALTER TABLE ocorrencias ADD COLUMN status TEXT")

    conn.commit()
    conn.close()
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # LOTES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        data TEXT,
        qtd_comprada INTEGER,
        qtd_recebida INTEGER,
        transporte TEXT
    )
    """)
    # ocorrencias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ocorrencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER,
        data TEXT,
        tipo TEXT,
        descricao TEXT,
        gravidade TEXT,
        custo REAL,
        dias_recuperacao INTEGER,
        status TEXT
    )
    """)
    def adicionar_coluna_se_nao_existir(cursor, tabela, coluna, tipo):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [c[1] for c in cursor.fetchall()]

    if coluna not in colunas:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
    # garantir que tabela existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS ocorrencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER,
    data TEXT,
    tipo TEXT,
    descricao TEXT,
    gravidade TEXT
)
""")

# MIGRAÇÃO SEGURA
adicionar_coluna_se_nao_existir(cursor, "ocorrencias", "custo", "REAL")
adicionar_coluna_se_nao_existir(cursor, "ocorrencias", "dias_recuperacao", "INTEGER")
adicionar_coluna_se_nao_existir(cursor, "ocorrencias", "status", "TEXT")
    
    # ANIMAIS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identificacao TEXT,
        idade INTEGER,
        lote_id INTEGER
    )
    """)

    # PESAGENS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pesagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER,
        peso REAL,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

# -----------------------
# LOTES
# -----------------------

def adicionar_lote(nome, descricao, data, qtd_comprada, qtd_recebida, transporte):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO lotes (nome, descricao, data, qtd_comprada, qtd_recebida, transporte)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, descricao, data, qtd_comprada, qtd_recebida, transporte))

    conn.commit()
    conn.close()


def listar_lotes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM lotes")
    dados = cursor.fetchall()

    conn.close()
    return dados


def obter_lote(lote_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM lotes WHERE id = ?
    """, (lote_id,))

    lote = cursor.fetchone()

    conn.close()
    return lote

# -----------------------
# ANIMAIS
# -----------------------

def adicionar_animal(identificacao, idade, lote_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO animais (identificacao, idade, lote_id)
    VALUES (?, ?, ?)
    """, (identificacao, idade, lote_id))

    conn.commit()
    conn.close()


def listar_animais():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM animais")
    dados = cursor.fetchall()

    conn.close()
    return dados


def listar_animais_por_lote(lote_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM animais WHERE lote_id = ?
    """, (lote_id,))

    dados = cursor.fetchall()

    conn.close()
    return dados


def contar_animais_no_lote(lote_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM animais WHERE lote_id = ?
    """, (lote_id,))

    total = cursor.fetchone()[0]

    conn.close()
    return total

# -----------------------
# PESAGENS
# -----------------------

def adicionar_pesagem(animal_id, peso, data):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO pesagens (animal_id, peso, data)
    VALUES (?, ?, ?)
    """, (animal_id, peso, data))

    conn.commit()
    conn.close()


def listar_pesagens(animal_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM pesagens WHERE animal_id = ?
    """, (animal_id,))

    dados = cursor.fetchall()

    conn.close()
    return dados
    

def adicionar_ocorrencia(animal_id, data, tipo, descricao, gravidade, custo, dias, status):
    conn = sqlite3.connect("rebanho.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ocorrencias
        (animal_id, data, tipo, descricao, gravidade, custo, dias_recuperacao, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (animal_id, data, tipo, descricao, gravidade, custo, dias, status))

    conn.commit()
    conn.close()

def listar_ocorrencias(animal_id):
    conn = sqlite3.connect("rebanho.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM ocorrencias WHERE animal_id = ?
    """, (animal_id,))

    dados = cursor.fetchall()
    conn.close()

    return dados
