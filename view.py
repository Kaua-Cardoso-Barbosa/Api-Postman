import os
import bcrypt

from flask import Flask, jsonify, request
from main import app, con
from funcao import gerar_hash_senha, senha_forte, verificar_senha
from fpdf import FPDF
from flask import send_file
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/livro', methods=['GET'])
def livro():
    try:
        cur = con.cursor()
        cur.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro")
        livro = cur.fetchall()
        livro_list = []
        for livro in livro:
            livro_list.append({
                'id_livro':livro[0]
                ,'titulo':livro[1]
                ,'autor':livro[2]
                ,'ano_publicacao':livro[3]
            })
        return jsonify(mensagem='Lista de livros', livro=livro_list)
    except Exception as e:
        return jsonify(mensagem=f"Erro ao consultar banco de dados: {e}"), 500
    finally:
        cur.close()
@app.route('/criar_livro', methods=['POST'])
def criar_livro():
    try:
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        ano_publicacao = request.form.get('ano_publicacao')
        imagem = request.files.get('imagem')


        cur = con.cursor()
        cur.execute("select 1 from livro where titulo = ?", (titulo,))
        if cur.fetchone():
            return jsonify({"error":"Livro já cadastrado"}), 400
        cur.execute("""insert into livro(titulo, autor, ano_publicacao) values (?, ?, ?) RETURNING id_livro """, (titulo, autor, ano_publicacao))

        codigo_livro = cur.fetchone()[0]
        con.commit()

        caminho_imagem =None
        if imagem:
            nome_imagem = f"{codigo_livro}.jpeg"
            caminho_imagem_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Livros")
            os.makedirs(caminho_imagem_destino, exist_ok=True)
            caminho_imagem = os.path.join(caminho_imagem_destino, nome_imagem)
            imagem.save(caminho_imagem)

        return jsonify({
            'message': "Livro cadastrado com sucesso!",
            'livro': {
                'titulo': titulo,
                'autor': autor,
                'ano_publicacao': ano_publicacao
            }
        }), 200

    except Exception as e:
        return jsonify(mensagem=f"Erro ao cadastrar livro: {e}"), 500
    finally:
        cur.close()

@app.route('/editar_livro/<int:id>', methods=['PUT'])
def editar_livro(id):

    cur = con.cursor()
    cur.execute("""select id_livro, titulo, autor, ano_publicacao from livro where id_livro=?""", (id,))
    tem_livro = cur.fetchone()
    if not tem_livro:
        cur.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get("ano_publicacao")

    cur.execute(""" update livro set titulo=?, autor=?, ano_publicacao=? where id_livro=?""", (titulo, autor, ano_publicacao, id))
    con.commit()
    con.close()

    return jsonify({"message": "Livro atualizado com sucesso",
                    'Livro':
                        {
                        'id_livro': id,
                        'titulo': titulo,
                        'autor': autor,
                        'ano_publicacao': ano_publicacao
                        }
                    })

@app.route('/excluir_livro/<int:id_livro>', methods=['delete'])
def excluir_livro(id_livro):
    cur = con.cursor()

    cur.execute("""select id_livro, titulo, autor, ano_publicacao from livro where id_livro=?""", (id_livro,))
    tem_livro = cur.fetchone()
    if not tem_livro:
        cur.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    cur.execute("""delete from livro where id_livro=?""", (id_livro,))

    con.commit()
    cur.close()
    return jsonify({'message': 'Livro exluido com sucesso', 'id_livro': id})

@app.route('/usuario', methods=['GET'])
def usuario():
    try:
        cur = con.cursor()
        cur.execute("SELECT id_usuario, nome, usuario, senha FROM usuario")
        usuario = cur.fetchall()
        usuario_list = []
        for usuario in usuario:
            usuario_list.append({
                'id_usuario':livro[0]
                ,'nome':livro[1]
                ,'usuario':livro[2]
                ,'senha':livro[3]
            })
        return jsonify(mensagem='Lista de usuario', livro=usuario_list)
    except Exception as e:
        return jsonify(mensagem=f"Erro ao consultar banco de dados: {e}"), 500
    finally:
        cur.close()

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    nome = data.get('nome')
    usuario = data.get('usuario')
    senha = data.get('senha')

    if not senha_forte(senha):
        return jsonify({
            "error": "Senha fraca. Use letras maiúsculas, minúsculas, números e caracteres especiais."
        }), 400

    senha_hash = gerar_hash_senha(senha)

    try:
        cur = con.cursor()
        cur.execute("select 1 from usuario where usuario = ?", (usuario,))
        if cur.fetchone():
            return jsonify({"error": "Usuario já cadastrado"}), 400

        cur.execute(
            "insert into usuario(nome, usuario, senha) values (?, ?, ?)",
            (nome, usuario, senha_hash)
        )

        con.commit()

        return jsonify({
            'message': "Usuario cadastrado com sucesso!",
            'usuario': {
                'nome': nome,
                'usuario': usuario,
                'senha': senha
            }
        }), 200

    except Exception as e:
        return jsonify(mensagem=f"Erro ao cadastrar usuario: {e}"), 500
    finally:
        cur.close()

@app.route('/editar_usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):

    cur = con.cursor()
    cur.execute(
        "select id_usuario, nome, usuario, senha from usuario where id_usuario=?",
        (id,)
    )
    usuario_existe = cur.fetchone()

    if not usuario_existe:
        cur.close()
        return jsonify({"error": "Usuario não encontrado"}), 404

    data = request.get_json()
    nome = data.get('nome')
    usuario = data.get('usuario')
    senha = data.get("senha")


    if senha:

        if not senha_forte(senha):
            cur.close()
            return jsonify({
                "error": "Senha fraca. Use letras maiúsculas, minúsculas, números e caracteres especiais."
            }), 400

        senha_hash = gerar_hash_senha(senha)

        cur.execute(
            "update usuario set nome=?, usuario=?, senha=? where id_usuario=?",
            (nome, usuario, senha_hash, id)
        )
    else:
        cur.execute(
            "update usuario set nome=?, usuario=? where id_usuario=?",
            (nome, usuario, id)
        )

    con.commit()
    cur.close()

    return jsonify({
        "message": "Usuario atualizado com sucesso",
        "usuario": {
            "id_usuario": id,
            "nome": nome,
            "usuario": usuario,
            "senha": senha
        }
    }), 200


@app.route('/excluir_usuario/<int:id_usuario>', methods=['delete'])
def excluir_usuario(id_usuario):
    cur = con.cursor()

    cur.execute("""select id_usuario, nome, usuario, senha from usuario where id_usuario=?""", (id_usuario,))

    usuario_existe = cur.fetchone()
    if not usuario_existe:
        cur.close()
        return jsonify({"error": "Usuario não encontrado"}), 404

    cur.execute("""delete from usuario where id_usuario=?""", (id_usuario,))

    con.commit()
    cur.close()
    return jsonify({'message': 'Usuario exluido com sucesso', 'id_usuario': id})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    usuario = data.get('usuario')
    senha = data.get('senha')

    if not usuario or not senha:
        return jsonify({"error": "Usuario e senha são obrigatórios"}), 400

    cur = con.cursor()
    cur.execute(
        "select id_usuario, nome, usuario, senha from usuario where usuario=?",
        (usuario,)
    )

    usuario_db = cur.fetchone()
    cur.close()

    if not usuario_db:
        return jsonify({"error": "Usuario ou senha inválidos"}), 401

    id_usuario, nome, usuario, senha_hash = usuario_db

    if not  (senha_hash):
        return jsonify({"error": "Usuario ou senha inválidos"}), 401

    return jsonify({
        "message": "Login realizado com sucesso",
        "usuario": {
            "id_usuario": id_usuario,
            "nome": nome,
            "usuario": usuario
        }
    }), 200

@app.route('/pfd_livro', methods=['GET'])
def pdf_livro():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livro", ln=True, align='C')

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)

    contador_livro = len(livros)
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livro}", ln=True, align='C')

    pdf_path = "relatorio_livro.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')

@app.route('/pfd_alunos', methods=['GET'])
def pdf_alunos():
    cursor = con.cursor()
    cursor.execute("SELECT id_usuario, nome, usuario FROM usuario")
    usuarios = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Usuario", ln=True, align='C')

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    for usuario in usuarios:
        pdf.cell(200, 10, f"ID: {usuario[0]} - {usuario[1]} - {usuario[2]} ", ln=True)

    contador_usuario = len(usuarios)
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de Usuario cadastrados: {contador_usuario}", ln=True, align='C')

    pdf_path = "relatorio_usuario.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')