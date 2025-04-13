#!/bin/bash

# Exit on any error
set -e

echo "=============================="
echo "Creating Django superuser"
echo "=============================="

# Prompt for superuser credentials
read -p "Username: " DJANGO_SUPERUSER_USERNAME
read -p "Email: " DJANGO_SUPERUSER_EMAIL
read -s -p "Password: " DJANGO_SUPERUSER_PASSWORD
echo
read -s -p "Confirm Password: " DJANGO_SUPERUSER_PASSWORD_CONFIRM
echo

# Check if passwords match
if [ "$DJANGO_SUPERUSER_PASSWORD" != "$DJANGO_SUPERUSER_PASSWORD_CONFIRM" ]; then
  echo "Passwords do not match. Aborting."
  exit 1
fi

# Run the Django createsuperuser command inside the container (non-interactive)
echo "Creating superuser..."
docker compose exec site python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser \"$DJANGO_SUPERUSER_USERNAME\" created successfully.')
else:
    print('Superuser \"$DJANGO_SUPERUSER_USERNAME\" already exists.')
" || { echo "Failed to create superuser"; exit 1; }

echo "Superuser creation process completed."
