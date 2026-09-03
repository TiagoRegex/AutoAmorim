import os
import sys
import mysql.connector

# Credenciais configuradas (testa primeiro a tua pass; se falhar, tenta sem pass)
SENHAS_MYSQL = ["123qwe", ""]


def obter_caminho_schema():
    """Localiza o ficheiro schema.sql em desenvolvimento ou empacotado no .exe."""
    if hasattr(sys, "_MEIPASS"):
        caminho = os.path.join(sys._MEIPASS, "database", "schema.sql")
        if os.path.exists(caminho):
            return caminho

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidatos = [
        os.path.join(base_dir, "database", "schema.sql"),
        os.path.join("database", "schema.sql"),
        "schema.sql",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None


def obter_conexao():
    """Retorna uma conexão ativa com a base de dados."""
    for pwd in SENHAS_MYSQL:
        try:
            return mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=pwd,
                database="autoamorim_db",
                use_pure=True,
            )
        except mysql.connector.Error as err:
            # 1045: Erro de password inválida; tenta a próxima da lista
            if err.errno == 1045:
                continue
            print(f"Erro ao ligar à BD: {err}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return None

    print("❌ Erro: Não foi possível autenticar no MySQL (verifique a senha).")
    return None


def inicializar_bd():
    """Garante que a BD, tabelas e utilizador padrão existem ao arrancar a app."""
    conexao = None
    senha_valida = None

    # 1. Determina a senha correta e cria a base de dados
    for pwd in SENHAS_MYSQL:
        try:
            conexao = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password=pwd,
                use_pure=True,
            )
            senha_valida = pwd
            break
        except mysql.connector.Error as err:
            if err.errno == 1045:
                continue
            print(f"❌ Erro de conexão ao MySQL: {err}")
            return
        except Exception as e:
            print(f"❌ Erro: {e}")
            return

    if not conexao:
        print("❌ Não foi possível ligar ao MySQL. O serviço está ativo?")
        return

    try:
        cursor = conexao.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS autoamorim_db")
        cursor.execute("USE autoamorim_db")

        caminho_sql = obter_caminho_schema()
        if caminho_sql and os.path.exists(caminho_sql):
            with open(caminho_sql, "r", encoding="utf-8") as f:
                sql_script = f.read()

            comandos = sql_script.split(";")
            for comando in comandos:
                linhas_limpas = [
                    linha
                    for linha in comando.splitlines()
                    if not linha.strip().startswith("--")
                ]
                comando_formatado = "\n".join(linhas_limpas).strip()

                if comando_formatado:
                    cursor.execute(comando_formatado)

            conexao.commit()
            print("✅ Base de dados e conta Admin sincronizadas com sucesso!")
        else:
            print(f"⚠️ Ficheiro schema.sql não encontrado em: {caminho_sql}")

        cursor.close()
        conexao.close()
    except Exception as err:
        print(f"❌ Erro ao executar schema.sql: {err}")