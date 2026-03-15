When you in your computer install this package:
$ mkdir devicemonitor
$ cd devicemonitor
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ python -m pip install django
(.venv) $ python -m pip install black
(.venv) $ django-admin startproject project_python_monitor .
(.venv) $ python manage.py startapp monitor

(.venv) $ pip install django-extensions
mkcert -install
mkcert localhost 127.0.0.1   # make certificate

# django_project/settings.py
INSTALLED_APPS = [
"django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'monitor',
    ]

# django_project/settings.py
TEMPLATES = [
	{
	...
	"DIRS": [BASE_DIR / "templates"], # new
	...
	},
	]

# django_project/settings.py
	"crispy_forms", # new
	"crispy_bootstrap5", # new
	"accounts",
	"pages",
	
# django_project/settings.py
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"	
CRISPY_TEMPLATE_PACK = "bootstrap5" 	
	


(.venv) $ python manage.py makemigrations
(.venv) $ python manage.py migrate



Start the Project
sudo .venv/bin/python manage.py runserver_plus --cert-file localhost+2.pem --key-file localhost+2-key.pem
