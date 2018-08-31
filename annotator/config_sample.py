DB_ENGINE = "django.db.backends.postgresql"
DB_HOST = "localhost"
DB_USER = "ex_user"
DB_USER_PASSWORD = "exegesis"
DB_NAME = "exegesis"
DB_PORT = "5432"

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'projects'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'Paste the key here'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'Paste the secret here'

USE_X_FORWARDED_HOST = True