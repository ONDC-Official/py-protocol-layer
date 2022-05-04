#run migration

uncomment # migrate = Migrate(app, db) in manage.py
```bash
export PYTHONPATH=.
export ENV=dev
export FLASK_APP=main/manage.py
flask db migrate

```

this will create migration directories in migration folder


Review the changes in upgrade

```bash
flask db upgrade
```
