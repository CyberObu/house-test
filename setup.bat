@echo off
echo ============================================
echo   NyumbaHub - Django Real Estate Setup
echo ============================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo [2/5] Installing dependencies...
pip install -r requirements.txt

echo [3/5] Running database migrations...
python manage.py makemigrations accounts properties agents dashboard blog core
python manage.py migrate

echo [4/5] Collecting static files...
python manage.py collectstatic --noinput

echo [5/5] Creating superuser...
echo Please create an admin account:
python manage.py createsuperuser

echo.
echo ============================================
echo   Setup complete! Run: python manage.py runserver
echo   Then visit: http://127.0.0.1:8000
echo   Admin panel: http://127.0.0.1:8000/admin
echo ============================================
pause
