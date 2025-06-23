# Internacionalização (i18n)

## Idiomas Suportados
- Português (pt)
- Inglês (en)
- Espanhol (es)

## Como adicionar um novo idioma
1. Adicione o idioma em `settings.py`.
2. Gere arquivos de tradução:
   ```bash
   python manage.py makemessages -l <idioma>
   ```
3. Traduza os textos em `locale/<idioma>/LC_MESSAGES/django.po`.
4. Compile as traduções:
   ```bash
   python manage.py compilemessages
   ```

## Dicas
- Use `gettext_lazy` para textos traduzíveis.
- Mantenha traduções atualizadas ao alterar textos no código. 