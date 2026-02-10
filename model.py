import fdb

class livro:
    def __init__(self, id_livro, titulo, autor, ano_publicacao):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao

class usuario:
    def __init__(self, id_usuario, nome, usuario, senha):
        self.id_usuario = id_usuario
        self.nome = nome
        self.usuario = usuario
        self.senha = senha