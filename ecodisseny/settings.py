from pathlib import Path
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = []

# Apps instaladas
INSTALLED_APPS = [
    'jazzmin',                          # Admin personalizado
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'maestros',
    'projectes',
    'pressupostos',
     "dal",
    "dal_select2",  # O el widget que prefieras
    'phonenumber_field',
    'accounts',
    "carregahores.apps.CarregahoresConfig",


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecodisseny.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Plantillas personalizadas
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecodisseny.wsgi.application'

# # Base de datos (MySQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT', cast=int),
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         }
#     }
# }

# Base de datos (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
    }
}

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'ca'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Campo ID por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Administració Ecodisseny",
    "site_header": "Ecodisseny",
    "site_brand": "Ecodisseny",
    "site_logo": "logo_ecodisseny_negatiu.png",       # archivo en static/
    "login_logo": "logo_ecodisseny_positiu.png",
    "login_logo_dark": "logo_ecodisseny_positiu.png",
    "site_logo_classes": "img-fluid sidebar-logo",
    "login_logo_classes": "img-fluid login-logo",      # ✅ NUEVA línea para el login
    "site_icon": "favicon.ico",                        # favicon en static/
    "welcome_sign": "Benvingut a l’administrador d’Ecodisseny!",
    "copyright": "©  Ecodisseny - By A.Rasmussen",
    "show_sidebar": True,
    "navigation_expanded": False,
    "group_models": True,
    "order_with_respect_to": [
        "projectes",
        "pressupostos",
         "pressupostos.PressupostPDFVersion",
        "maestros",
        "maestros.Clients",
        "maestros.DepartamentClient",
        "maestros.PersonaContactClient",
        "maestros.Parroquia",
        "maestros.Poblacio",
        "maestros.Ubicacio",
        "maestros.Tipusrecurso",
        "maestros.Recurso",
        "maestros.Treballs",
        "maestros.Tasca",
        "maestros.TasquesTreball",
        "maestros.Desplacaments",
        "maestros.Hores",
         "auth",

    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "maestros": "fas fa-cube",
        "maestros.Clients": "fas fa-building",
        "maestros.Tasca": "fas fa-tasks",
        "maestros.Treballs": "fas fa-trowel-bricks",
        "maestros.TasquesTreball": "fas fa-wrench",
        "maestros.Desplacaments": "fas fa-car",
        "maestros.Hores": "fas fa-clock",
        "maestros.Recurso": "fas fa-cogs",
        "maestros.Tipusrecurso": "fas fa-cogs",
        "maestros.DepartamentClient": "fas fa-building",
        "maestros.PersonaContactClient": "fas fa-building-user",
        "maestros.Parroquia": "fas fa-map-marker-alt",
        "maestros.Poblacio": "fas fa-map-marker-alt",
        "maestros.Ubicacio": "fas fa-map-marker-alt",
        "pressupostos.Pressupostos": "fas fa-file-invoice",
        "projectes": "fas fa-project-diagram",
        "projectes.Projectes": "fas fa-project-diagram",
    },
    "topmenu_links": [
        {"name": "Inici", "url": "/", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "auth"},
        # Enlace al dashboard del admin
        {"name": "Admin", "url": "admin:index", "permissions": ["auth.view_user"]},
        # Enlace personalizado a test_base
        {"name": "Pressupostos", "url": "/pressupostos/list", "new_window": True},
    ],
    "usermenu_links": [
        {"name": "Ajuda", "url": "https://ecodisseny.cat/ajuda", "new_window": True},
    ],
    "related_modal_active": True,

    "show_ui_builder": False,

    # ✅ CSS personalizado para limitar tamaño del logo en login/logout
    "custom_css": "css/admin_custom.css",
    
}



# Ajustes de estilo Jazzmin
JAZZMIN_UI_TWEAKS = {}



LOGIN_REDIRECT_URL = '/'  # Redirección directa a la página de inicio
LOGOUT_REDIRECT_URL = '/accounts/login/'

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@ecodisseny.local"


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu@email.com'
# EMAIL_HOST_PASSWORD = 'tu_contraseña'
# DEFAULT_FROM_EMAIL = 'webmaster@example.com'
