def validar_cpf(cpf):
    """
    Retorna o CPF válido ou False.
    """
    import re

    if len(cpf) < 11:
        return False

    if cpf in [s * 11 for s in [str(n) for n in range(10)]]:
        return False

    calc = [i for i in range(1, 10)]
    d1 = (sum([int(a) * b for a, b in zip(cpf[:-2], calc)]) % 11) % 10
    d2 = (sum([int(a) * b for a, b in zip(reversed(cpf[:-2]), calc)]) % 11) % 10
    return str(d1) == cpf[-2] and str(d2) == cpf[-1]


def validar_data(data):
    data_valida = True
    split_data = data.split("/")
    mes = int(split_data[1])
    dia = int(split_data[0])
    if (mes > 12 and mes < 1) or (dia > 30 and dia < 1) or (mes == int(2) and dia > 29):
        data_valida = False
    return data_valida


def idade(born):
    """Função para descobrir a idade de uma pessoa

    Args:
        born ([date]): [Data da pessoa]

    Returns:
        [int]: [Idade da pessoa]
    """
    from datetime import date

    try:
        if born:
            born = born.replace("-", "/")
            born = born.split("/")
            year = int(born[2])
            month = int(born[1])
            day = int(born[0])
            today = date.today()
            return today.year - year - ((today.month, today.day) < (month, day))
    except Exception:
        return None
