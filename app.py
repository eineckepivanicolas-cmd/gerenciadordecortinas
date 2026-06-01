import sqlite3

def criar_banco():
    conn = sqlite3.connect("banco.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instalacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        endereco TEXT,
        numero TEXT,
        valor REAL,
        data TEXT,
        observacoes TEXT,
        ambientes INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ambientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instalacao_id INTEGER,
        nome TEXT,
        tipo TEXT,
        automatizada TEXT,
        largura REAL,
        altura REAL,
        tipo_persiana TEXT,
        lado_comando TEXT,
        bando TEXT,
        nivelador TEXT,
        FOREIGN KEY (instalacao_id)
            REFERENCES instalacoes(id)
            ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

def conectar():
    conn = sqlite3.connect("banco.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@app.route("/instalacoes", methods=["GET"])
def listar_instalacoes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM instalacoes
    ORDER BY id DESC
    """)

    instalacoes = cursor.fetchall()

    resultado = []

    for inst in instalacoes:

        cursor.execute("""
        SELECT
            nome,
            tipo,
            automatizada,
            largura,
            altura,
            tipo_persiana, 
            lado_comando,
            bando,
            nivelador
            
        FROM ambientes
        WHERE instalacao_id = ?
        """, (inst[0],))

        ambientes = cursor.fetchall()

        ambientes_detalhados = []

        for ambiente in ambientes:
            ambientes_detalhados.append({
                "nome": ambiente[0],
                "tipo": ambiente[1],
                "automatizada": ambiente[2],
                "largura": ambiente[3],
                "altura": ambiente[4],
                "tipo_persiana": ambiente[5],
                "lado_comando": ambiente[6],
                "bando": ambiente[7],
                "nivelador": ambiente[8]

            })

        resultado.append({
            "id": inst[0],
            "nome": inst[1],
            "endereco": inst[2],
            "numero": inst[3],
            "valor": inst[4],
            "data": inst[5],
            "observacoes": inst[6],
            "ambientes": inst[7],
            "ambientesDetalhados": ambientes_detalhados
        })

    conn.close()

    return jsonify(resultado)

@app.route("/instalacoes", methods=["POST"])
def criar_instalacao():

    dados = request.json

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO instalacoes
    (
        nome,
        endereco,
        numero,
        valor,
        data,
        observacoes,
        ambientes
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["nome"],
        dados["endereco"],
        dados["numero"],
        dados["valor"],
        dados["data"],
        dados["observacoes"],
        dados["ambientes"]
    ))

    instalacao_id = cursor.lastrowid

    for ambiente in dados["ambientesDetalhados"]:

        cursor.execute("""
       INSERT INTO ambientes
(
        instalacao_id,
        nome,
        tipo,
        automatizada,
        largura,
        altura,
        tipo_persiana,
        lado_comando,
        bando,
        nivelador
)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            instalacao_id,
            ambiente["nome"],
            ambiente["tipo"],
            ambiente["automatizada"],
            ambiente["largura"],
            ambiente["altura"],
            ambiente.get("tipo_persiana"),
            ambiente.get("lado_comando"),
            ambiente.get("bando"),
            ambiente.get("nivelador")

        ))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Instalação cadastrada com sucesso"
    })
@app.route("/")
def home():
   return render_template("index.html")
@app.route("/instalacoes/<int:id>", methods=["DELETE"])
def excluir_instalacao(id):

    conn = conectar()
    cursor = conn.cursor()

    # Exclui primeiro os ambientes da instalação
    cursor.execute("""
    DELETE FROM ambientes
    WHERE instalacao_id = ?
    """, (id,))

    # Exclui a instalação
    cursor.execute("""
    DELETE FROM instalacoes
    WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Instalação excluída com sucesso"
    })
@app.route("/instalacoes/<int:id>", methods=["PUT"])
def atualizar_instalacao(id):

    dados = request.json

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE instalacoes
    SET
        nome=?,
        endereco=?,
        numero=?,
        valor=?,
        data=?,
        observacoes=?,
        ambientes=?
    WHERE id=?
    """,(
        dados["nome"],
        dados["endereco"],
        dados["numero"],
        dados["valor"],
        dados["data"],
        dados["observacoes"],
        dados["ambientes"],
        id
    ))

    cursor.execute("""
    DELETE FROM ambientes
    WHERE instalacao_id=?
    """, (id,))

    for ambiente in dados["ambientesDetalhados"]:

      cursor.execute("""
INSERT INTO ambientes
(
    instalacao_id,
    nome,
    tipo,
    automatizada,
    largura,
    altura,
    tipo_persiana,
    lado_comando,
    bando,
    nivelador
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    id,
    ambiente["nome"],
    ambiente["tipo"],
    ambiente["automatizada"],
    ambiente["largura"],
    ambiente["altura"],
    ambiente.get("tipo_persiana"),
    ambiente.get("lado_comando"),
    ambiente.get("bando"),
    ambiente.get("nivelador")
))
        

    conn.commit()
    conn.close()

    return jsonify({
        "mensagem": "Instalação atualizada com sucesso"
    })
if __name__ == "__main__":
    criar_banco()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)