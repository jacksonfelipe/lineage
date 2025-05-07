from apps.main.home.models import Conquista, ConquistaUsuario
from .validators import VALIDADORES_CONQUISTAS


def verificar_conquistas(user, request=None):
    conquistas_ganhas = []
    
    for codigo, func_validadora in VALIDADORES_CONQUISTAS.items():
        if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo=codigo).exists():
            if func_validadora(user, request=request):
                conquista = Conquista.objects.filter(codigo=codigo).first()
                if conquista:
                    ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
                    conquistas_ganhas.append(conquista)

    return conquistas_ganhas
