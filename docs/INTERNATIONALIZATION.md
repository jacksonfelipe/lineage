# Internationalization (i18n)

## Supported Languages
- Portuguese (pt)
- English (en)
- Spanish (es)

## How to add a new language
1. Add the language in `settings.py`.
2. Generate translation files:
   ```bash
   python manage.py makemessages -l <language>
   ```
3. Translate the texts in `locale/<language>/LC_MESSAGES/django.po`.
4. Compile the translations:
   ```bash
   python manage.py compilemessages
   ```

## Tips
- Use `gettext_lazy` for translatable texts.
- Keep translations updated when changing texts in the code. 