# Fairmatic
Dashboard for user management and much more

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

this is will apply the migration changes

```buildoutcfg
alter table fleet_drivers drop constraint fleet_drivers_email_key
```

```bash
CLAIMS_REDSHIFT_SQLALCHEMY_URI = 'postgresql://claimsapp:c@fairmatic-dev.cts8t7zu6o9h.us-west-2.redshift.amazonaws.com:5439/fairmatic'
```

# Way to insert broadspire data into redshift
```bash
# port forward the redshift to local 
# set env tp dev
# copy the latest id/email in fm-ses-inbox
# call adhoc_s3_broadspire_insertion(<id-copied-in-above-step>)
```