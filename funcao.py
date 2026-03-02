from email.mime.multipart import MIMEMultipart

import bcrypt
import re

import smtplib
from email.mime.text import MIMEText

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
