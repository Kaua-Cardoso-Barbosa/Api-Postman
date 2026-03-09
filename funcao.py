from email.mime.multipart import MIMEMultipart

import bcrypt
import re

import smtplib
from email.mime.text import MIMEText

import jwt
import datetime
from main import app

senha_secreta = app.config['SECRET_KEY']

def gerar_token(id_usuario):
    payload = {'id_usuario': id_usuario, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=20)}
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')

    return token


def remover_bearer(token):
    if token.startswith('Bearer '):
        return token[len('Bearer '):]
    else:
        return token

def enviando_email(destinatario, assunto, mensagem):
    user = 'kauacardosobarbosasenai@gmail.com'
    senha = 'oslq efdy idrb qrtx'

    msg = MIMEText(mensagem)
    msg['From'] = user
    msg['To'] = destinatario
    msg['Subject'] = assunto

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, senha)
    server.send_message(msg)
    server.quit()

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
