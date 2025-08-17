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
