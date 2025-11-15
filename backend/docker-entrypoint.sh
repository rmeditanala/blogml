#!/bin/sh

# Handle Docker secrets and set environment variables
if [ -f "/run/secrets/mysql_password" ]; then
    export DB_PASSWORD="$(cat /run/secrets/mysql_password)"
    echo "MySQL password loaded from secret"
fi

if [ -f "/run/secrets/app_key" ]; then
    export APP_KEY="$(cat /run/secrets/app_key)"
    echo "APP_KEY loaded from secret"
fi

if [ -f "/run/secrets/mail_password" ]; then
    export MAIL_PASSWORD="$(cat /run/secrets/mail_password)"
    echo "Mail password loaded from secret"
fi

# Run Laravel optimizations
php artisan config:cache --no-interaction
php artisan route:cache --no-interaction
php artisan view:cache --no-interaction

# Execute the original command
exec "$@"