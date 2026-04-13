import sqlite3

def conectar():
    return sqlite3.connect("data.db", check_same_thread=False)

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identificacao TEXT,
        idade INTEGER,
        peso REAL,
        data_pesagem TEXT
    )
    """)

    conn.commit()
    conn.close()

def adicionar_animal(identificacao, idade, peso, data):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO animais (identificacao, idade, peso, data_pesagem)
    VALUES (?, ?, ?, ?)
    """, (identificacao, idade, peso, data))

    conn.commit()
    conn.close()

def listar_animais():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM animais")
    dados = cursor.fetchall()

    conn.close()
    return dados
