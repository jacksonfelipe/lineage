from django.core.exceptions import ValidationError
from django.utils.translation import get_language_from_request
import re


def remove_cpf_mask(cpf):
    """
    Remove a máscara do CPF, deixando apenas os números.

    Args:
        cpf (str): CPF no formato com máscara (ex: '123.456.789-09').

    Returns:
        str: CPF sem máscara (ex: '12345678909').
    """
    if not cpf:
        return ""
    return re.sub(r'\D', '', cpf)


def validate_cpf(value):
    """
    Validação de CPF com algoritmo de verificação.
    """
    # Remover caracteres especiais
    cpf = ''.join(filter(str.isdigit, value))
    
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos')

    if cpf in [str(i)*11 for i in range(10)]:
        raise ValidationError('CPF inválido')
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        sum = 0
        for j in range(0, i):
            sum += int(cpf[j]) * ((i+1) - j)
        check_digit = ((sum * 10) % 11) % 10
        if check_digit != int(cpf[i]):
            raise ValidationError('CPF inválido')


def verificar_conquistas(request):
    from .models import Conquista, ConquistaUsuario, AddressUser
    from apps.main.solicitation.models import Solicitation
    from apps.main.message.models import Friendship

    user = request.user

    conquistas = []

    # Exemplo 1: Primeira vez logando
    if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='primeiro_login').exists():
        conquista = Conquista.objects.filter(codigo='primeiro_login').first()  # Usa filter ao invés de get
        if conquista:
            ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
            conquistas.append(conquista)

    # Exemplo 2: Criou 10 leilões
    if user.auctions.count() >= 10:  # Alteração aqui para usar 'auctions'
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='10_leiloes').exists():
            conquista = Conquista.objects.filter(codigo='10_leiloes').first()  # Usa filter ao invés de get
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 3: Primeira solicitação enviada
    if Solicitation.objects.filter(user=user).count() >= 1:
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='primeira_solicitacao').exists():
            conquista = Conquista.objects.filter(codigo='primeira_solicitacao').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 4: Editou o avatar
    user_avatar = getattr(user, 'avatar', None)  # Ajuste para o seu campo de avatar, se for um Profile
    if user_avatar and not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='avatar_editado').exists():
        conquista = Conquista.objects.filter(codigo='avatar_editado').first()
        if conquista:
            ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
            conquistas.append(conquista)

    # Exemplo 5: Cadastrou endereço
    if AddressUser.objects.filter(user=user).exists():
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='endereco_cadastrado').exists():
            conquista = Conquista.objects.filter(codigo='endereco_cadastrado').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 6: Verificou e-mail
    if user.is_email_verified:
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='email_verificado').exists():
            conquista = Conquista.objects.filter(codigo='email_verificado').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 7: Ativou 2FA
    if hasattr(user, 'is_2fa_enabled') and user.is_2fa_enabled:
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='2fa_ativado').exists():
            conquista = Conquista.objects.filter(codigo='2fa_ativado').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 8: Trocou de idioma (cookie django_language foi definido)
    if hasattr(user, 'perfilgamer') and user.perfilgamer and ConquistaUsuario.objects.filter(usuario=user).count() > 0:
        idioma = get_language_from_request(request)
        if idioma and not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='idioma_trocado').exists():
            conquista = Conquista.objects.filter(codigo='idioma_trocado').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 9: Enviou primeiro pedido de amizade
    if Friendship.objects.filter(user=user).exists():
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='primeiro_amigo').exists():
            conquista = Conquista.objects.filter(codigo='primeiro_amigo').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    # Exemplo 10: Aceitou o primeiro pedido de amizade
    if Friendship.objects.filter(user=user, accepted=True).exists():
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo='primeiro_amigo_aceito').exists():
            conquista = Conquista.objects.filter(codigo='primeiro_amigo_aceito').first()
            if conquista:
                ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                conquistas.append(conquista)

    return conquistas
