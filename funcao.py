import bcrypt
import re

def gerar_hash_senha(senha):
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_senha = bcrypt.hashpw(senha_bytes, salt)
    return hash_senha

def verificar_senha(senha_digitada, hash_salvo):
    return bcrypt.checkpw(
        senha_digitada.encode('utf-8'),
        hash_salvo
    )

def senha_forte(senha):
    if len(senha) < 8:
        return False
    if not re.search(r"[A-Z]", senha):
        return False
    if not re.search(r"[a-z]", senha):
        return False
    if not re.search(r"\d", senha):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return False
    return True
