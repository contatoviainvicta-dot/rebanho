import sqlite3

def conectar():
    return sqlite3.connect("data.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # tabela animais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identificacao TEXT,
        idade INTEGER
    )
    """)

    # tabela pesagens
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
# ANIMAIS
# -----------------------

def adicionar_animal(identificacao, idade):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO animais (identificacao, idade)
    VALUES (?, ?)
    """, (identificacao, idade))

    conn.commit()
    conn.close()

def listar_animais():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM animais")
    dados = cursor.fetchall()

    conn.close()
    return dados


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
