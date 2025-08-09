"""
Validadores e processadores de mídia para redes sociais
"""
import os
from PIL import Image, ImageOps
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext as _
import tempfile
import subprocess


# ============================================================================
# CONFIGURAÇÕES DE MÍDIA PARA REDES SOCIAIS
# ============================================================================

# Tamanhos máximos de arquivo (em MB)
MAX_IMAGE_SIZE_MB = 10  # 10MB para imagens
MAX_VIDEO_SIZE_MB = 100  # 100MB para vídeos
MAX_AVATAR_SIZE_MB = 5   # 5MB para avatares

# Resoluções máximas
MAX_IMAGE_WIDTH = 1920
MAX_IMAGE_HEIGHT = 1080
MAX_VIDEO_WIDTH = 1920
MAX_VIDEO_HEIGHT = 1080

# Formatos permitidos
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP', 'GIF']
ALLOWED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.webm']

# Durações máximas para vídeos (em segundos)
MAX_VIDEO_DURATION = 300  # 5 minutos
MAX_SHORT_VIDEO_DURATION = 60  # 1 minuto para vídeos curtos


# ============================================================================
# VALIDADORES DE IMAGEM
# ============================================================================

def validate_image_size(image):
    """Valida o tamanho do arquivo de imagem"""
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            _('A imagem é muito grande. Tamanho máximo permitido: %(max_size)sMB') % {
                'max_size': MAX_IMAGE_SIZE_MB
            }
        )


def validate_avatar_size(image):
    """Valida o tamanho do arquivo de avatar"""
    if image.size > MAX_AVATAR_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            _('O avatar é muito grande. Tamanho máximo permitido: %(max_size)sMB') % {
                'max_size': MAX_AVATAR_SIZE_MB
            }
        )


def validate_image_format(image):
    """Valida o formato da imagem"""
    try:
        with Image.open(image) as img:
            if img.format not in ALLOWED_IMAGE_FORMATS:
                raise ValidationError(
                    _('Formato de imagem não suportado. Formatos permitidos: %(formats)s') % {
                        'formats': ', '.join(ALLOWED_IMAGE_FORMATS)
                    }
                )
    except Exception:
        raise ValidationError(_('Arquivo de imagem inválido ou corrompido.'))


def validate_image_dimensions(image):
    """Valida as dimensões da imagem"""
    try:
        with Image.open(image) as img:
            width, height = img.size
            if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
                raise ValidationError(
                    _('Imagem muito grande. Dimensões máximas: %(width)sx%(height)s pixels') % {
                        'width': MAX_IMAGE_WIDTH,
                        'height': MAX_IMAGE_HEIGHT
                    }
                )
    except Exception:
        raise ValidationError(_('Não foi possível validar as dimensões da imagem.'))


def validate_image_content(image):
    """Valida se a imagem não contém conteúdo suspeito baseado em metadados"""
    try:
        with Image.open(image) as img:
            # Verificar se a imagem tem dimensões válidas
            if img.size[0] < 1 or img.size[1] < 1:
                raise ValidationError(_('Imagem com dimensões inválidas.'))
            
            # Verificar se não é uma imagem muito pequena (possível spam)
            if img.size[0] < 50 and img.size[1] < 50:
                raise ValidationError(_('Imagem muito pequena. Mínimo: 50x50 pixels.'))
                
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(_('Erro ao processar a imagem.'))


# ============================================================================
# VALIDADORES DE VÍDEO
# ============================================================================

def validate_video_size(video):
    """Valida o tamanho do arquivo de vídeo"""
    if video.size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            _('O vídeo é muito grande. Tamanho máximo permitido: %(max_size)sMB') % {
                'max_size': MAX_VIDEO_SIZE_MB
            }
        )


def validate_video_format(video):
    """Valida o formato do vídeo"""
    file_extension = os.path.splitext(video.name)[1].lower()
    if file_extension not in ALLOWED_VIDEO_FORMATS:
        raise ValidationError(
            _('Formato de vídeo não suportado. Formatos permitidos: %(formats)s') % {
                'formats': ', '.join(ALLOWED_VIDEO_FORMATS)
            }
        )


def validate_video_duration(video):
    """Valida a duração do vídeo usando ffprobe"""
    try:
        # Salvar temporariamente o arquivo para análise
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video.name)[1]) as temp_file:
            for chunk in video.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Usar ffprobe para obter informações do vídeo
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format',
                temp_file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                video_info = json.loads(result.stdout)
                duration = float(video_info['format']['duration'])
                
                if duration > MAX_VIDEO_DURATION:
                    raise ValidationError(
                        _('Vídeo muito longo. Duração máxima: %(max_duration)s segundos (%(max_minutes)s minutos)') % {
                            'max_duration': MAX_VIDEO_DURATION,
                            'max_minutes': MAX_VIDEO_DURATION // 60
                        }
                    )
            else:
                # Se ffprobe falhar, usar validação básica por tamanho
                pass
                
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # ffprobe não disponível ou falhou, usar validação básica
            pass
            
    except Exception:
        raise ValidationError(_('Erro ao validar o vídeo.'))
    finally:
        # Limpar arquivo temporário
        try:
            os.unlink(temp_file_path)
        except:
            pass


# ============================================================================
# PROCESSADORES DE IMAGEM
# ============================================================================

def process_image_for_social_media(image_path, output_path=None, max_width=1200, max_height=1200, quality=85):
    """
    Processa imagem para otimização em redes sociais
    - Redimensiona mantendo proporção
    - Otimiza qualidade
    - Remove metadados EXIF
    - Converte para formato web-friendly
    """
    try:
        with Image.open(image_path) as img:
            # Remover informações EXIF (privacidade)
            img = ImageOps.exif_transpose(img)
            
            # Converter para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar mantendo proporção
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Definir caminho de saída
            if not output_path:
                output_path = image_path
            
            # Salvar com otimização
            img.save(output_path, 'JPEG', quality=quality, optimize=True, progressive=True)
            
        return output_path
        
    except Exception as e:
        raise ValidationError(_('Erro ao processar a imagem: %(error)s') % {'error': str(e)})


def process_avatar_image(image_path, output_path=None, size=400):
    """
    Processa imagem para avatar
    - Redimensiona para tamanho quadrado
    - Otimiza para web
    """
    try:
        with Image.open(image_path) as img:
            # Remover EXIF
            img = ImageOps.exif_transpose(img)
            
            # Converter para RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar para quadrado (crop central se necessário)
            img = ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS)
            
            if not output_path:
                output_path = image_path
            
            img.save(output_path, 'JPEG', quality=90, optimize=True)
            
        return output_path
        
    except Exception as e:
        raise ValidationError(_('Erro ao processar o avatar: %(error)s') % {'error': str(e)})


def create_image_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    """Cria thumbnail da imagem"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
        return thumbnail_path
    except Exception as e:
        raise ValidationError(_('Erro ao criar thumbnail: %(error)s') % {'error': str(e)})


# ============================================================================
# PROCESSADORES DE VÍDEO
# ============================================================================

def process_video_for_social_media(video_path, output_path=None, max_duration=None):
    """
    Processa vídeo para redes sociais usando ffmpeg
    - Comprime para web
    - Reduz resolução se necessário
    - Corta duração se especificado
    """
    try:
        if not output_path:
            name, ext = os.path.splitext(video_path)
            output_path = f"{name}_processed{ext}"
        
        # Comando básico do ffmpeg para otimização web
        cmd = [
            'ffmpeg', '-i', video_path,
            '-c:v', 'libx264',  # Codec de vídeo H.264
            '-preset', 'medium',  # Preset de velocidade/qualidade
            '-crf', '23',  # Qualidade (0-51, menor = melhor qualidade)
            '-c:a', 'aac',  # Codec de áudio
            '-b:a', '128k',  # Bitrate do áudio
            '-movflags', '+faststart',  # Otimização para streaming
            '-y',  # Sobrescrever arquivo de saída
        ]
        
        # Adicionar limitação de duração se especificada
        if max_duration:
            cmd.extend(['-t', str(max_duration)])
        
        # Adicionar filtro de escala se necessário
        cmd.extend(['-vf', f'scale={MAX_VIDEO_WIDTH}:{MAX_VIDEO_HEIGHT}:force_original_aspect_ratio=decrease'])
        
        cmd.append(output_path)
        
        # Executar ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise ValidationError(_('Erro ao processar vídeo: %(error)s') % {'error': result.stderr})
        
        return output_path
        
    except subprocess.TimeoutExpired:
        raise ValidationError(_('Processamento de vídeo demorou muito tempo.'))
    except FileNotFoundError:
        raise ValidationError(_('FFmpeg não encontrado. Não é possível processar vídeos.'))
    except Exception as e:
        raise ValidationError(_('Erro ao processar vídeo: %(error)s') % {'error': str(e)})


def create_video_thumbnail(video_path, thumbnail_path, time_position='00:00:01'):
    """Cria thumbnail do vídeo"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-ss', time_position,
            '-vframes', '1',
            '-q:v', '2',
            '-y',
            thumbnail_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise ValidationError(_('Erro ao criar thumbnail do vídeo.'))
        
        return thumbnail_path
        
    except Exception as e:
        raise ValidationError(_('Erro ao criar thumbnail do vídeo: %(error)s') % {'error': str(e)})


# ============================================================================
# VALIDADORES COMBINADOS
# ============================================================================

def validate_social_media_image(image):
    """Validador completo para imagens em redes sociais"""
    validate_image_size(image)
    validate_image_format(image)
    validate_image_dimensions(image)
    validate_image_content(image)


def validate_social_media_video(video):
    """Validador completo para vídeos em redes sociais"""
    validate_video_size(video)
    validate_video_format(video)
    validate_video_duration(video)


def validate_avatar_image(image):
    """Validador completo para avatares"""
    validate_avatar_size(image)
    validate_image_format(image)
    validate_image_content(image)


# ============================================================================
# UTILITÁRIOS
# ============================================================================

def get_image_info(image_path):
    """Retorna informações básicas da imagem"""
    try:
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.size[0],
                'height': img.size[1],
                'has_transparency': img.mode in ('RGBA', 'LA', 'P'),
            }
    except Exception:
        return None


def get_video_info(video_path):
    """Retorna informações básicas do vídeo usando ffprobe"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', video_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            video_stream = None
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if video_stream:
                return {
                    'duration': float(info['format'].get('duration', 0)),
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'codec': video_stream.get('codec_name'),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'bitrate': int(info['format'].get('bit_rate', 0)),
                }
        
        return None
        
    except Exception:
        return None


def is_image_safe_for_work(image_path):
    """
    Placeholder para detecção de conteúdo NSFW
    Pode ser integrado com APIs como Google Vision, AWS Rekognition, etc.
    """
    # Por enquanto, sempre retorna True
    # Em produção, aqui seria feita a análise real da imagem
    return True


def detect_faces_in_image(image_path):
    """
    Placeholder para detecção de faces
    Útil para moderação e funcionalidades de tag de pessoas
    """
    # Implementação futura com bibliotecas como face_recognition ou APIs
    return []
