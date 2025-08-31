Web: python manage.py migrate && python manage.py runserver 0.0.0.0:${PORT}
webb: python manage.py migrate && gunicorn GesStockBackend.wsgi --timeout 60 --workers 2 --log-file -