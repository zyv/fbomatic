# fbomatic

Provisions for having multiple pumps are currently in place, but they are not actually supported.

## Develop

```
./manage.py makemessages -l de
./manage.py createsuperuser
./manage.py makemigrations
./manage.py makemessages -a
./manage.py compilemessages
```

## Deploy

```
./manage.py migrate
./manage.py createinitialrevisions
./manage.py compilemessages
./manage.py collectstatic
```
