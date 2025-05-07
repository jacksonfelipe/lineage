from .validators import registrar_validador
from apps.main.home.models import AddressUser
from apps.main.solicitation.models import Solicitation
from apps.main.message.models import Friendship
from django.utils.translation import get_language_from_request


@registrar_validador('primeiro_login')
def primeiro_login(user, request=None):
    return True  # Apenas logar

@registrar_validador('10_leiloes')
def dez_leiloes(user, request=None):
    return user.auctions.count() >= 10

@registrar_validador('primeira_solicitacao')
def primeira_solicitacao(user, request=None):
    return Solicitation.objects.filter(user=user).exists()

@registrar_validador('avatar_editado')
def avatar_editado(user, request=None):
    return bool(getattr(user, 'avatar', None))

@registrar_validador('endereco_cadastrado')
def endereco(user, request=None):
    return AddressUser.objects.filter(user=user).exists()

@registrar_validador('email_verificado')
def email_verificado(user, request=None):
    return getattr(user, 'is_email_verified', False)

@registrar_validador('2fa_ativado')
def dois_fatores(user, request=None):
    return getattr(user, 'is_2fa_enabled', False)

@registrar_validador('idioma_trocado')
def idioma(user, request=None):
    if not request:
        return False
    idioma = get_language_from_request(request)
    return idioma != 'pt-br'  # ou qualquer padrão

@registrar_validador('primeiro_amigo')
def primeiro_amigo(user, request=None):
    return Friendship.objects.filter(user=user).exists()

@registrar_validador('primeiro_amigo_aceito')
def primeiro_amigo_aceito(user, request=None):
    return Friendship.objects.filter(user=user, accepted=True).exists()
