# fbomatic

Provisions for having multiple pumps are currently in place, but they are not actually supported.

## Develop

```
./manage.py makemessages -l de
./manage.py createsuperuser
./manage.py makemigrations
./manage.py makemessages -a
```

## Deploy

```shell
# For passenger
apt install python-is-python3

# For mysqlclient
apt install build-essential pkg-config default-libmysqlclient-dev

# For python manage.py compilemessages
apt install gettext
```

Install uv:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Adjust `fbomatic.env`:

```shell
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

```python
from django.core.management.utils import get_random_secret_key

print(get_random_secret_key())

from urllib.parse import quote

quote("password")
```
