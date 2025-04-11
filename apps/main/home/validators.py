import re
from django.core.exceptions import ValidationError


def validate_ascii_username(value):
    if not re.fullmatch(r'[A-Za-z0-9]+', value):
        raise ValidationError('O nome de usuário deve conter apenas letras e números (sem espaços ou símbolos).')
