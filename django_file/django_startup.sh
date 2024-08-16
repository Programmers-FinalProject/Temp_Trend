cd /home/junghwa010609/django &&
cd django_file &&
source venv/bin/activate &&
python manage.py makemigrations --merge --noinput &&
python manage.py migrate &&
python manage.py collectstatic --noinput &&
python manage.py process_tasks
sudo systemctl restart gunicorn &&
sudo systemctl restart nginx &&
