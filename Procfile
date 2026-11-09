web: gunicorn realestate.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
release: mkdir -p staticfiles && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
