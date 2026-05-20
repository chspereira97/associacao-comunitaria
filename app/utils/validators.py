import re
from datetime import date

def validar_email(email):
    """Valida se o e-mail tem formato válido"""
    if not email or email.strip() == '':
        return True
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_telefone(telefone):
    """Valida se o telefone tem APENAS números e pelo menos 8 dígitos"""
    if not telefone or telefone.strip() == '':
        return True
    numeros = re.sub(r'[^0-9]', '', telefone)
    return len(numeros) >= 8 and numeros.isdigit()

def validar_cpf(cpf):
    """Valida se o CPF tem APENAS números e exatamente 11 dígitos"""
    if not cpf or cpf.strip() == '':
        return True
    numeros = re.sub(r'[^0-9]', '', cpf)
    return len(numeros) == 11 and numeros.isdigit()

def validar_data_nascimento(dia, mes, ano):
    """Valida se a data de nascimento é válida e tem entre 6 e 100 anos"""
    try:
        data_nasc = date(ano, mes, dia)
        hoje = date.today()
        if data_nasc > hoje:
            return False, "A data de nascimento não pode ser no futuro!"
        idade = hoje.year - data_nasc.year
        if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
            idade -= 1
        if idade < 6:
            return False, f"O aluno deve ter pelo menos 6 anos! (Idade calculada: {idade} anos)"
        if idade > 100:
            return False, f"Idade máxima permitida é 100 anos! (Idade calculada: {idade} anos)"
        return True, data_nasc
    except ValueError:
        return False, "Data de nascimento inválida!"