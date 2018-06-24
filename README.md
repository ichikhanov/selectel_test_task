# Summary
## Simple ticket system api project written with python2, psycopg2, Flask

## Steps for launch in dev
1. make virtualenv 
```virtualenv -p python --prompt="(prompt_name)" env_folder```

2. activate it

3. install requrements
```pip isntall -r requirements.txt```

4. run docker conteiner for postgres or install server and create database scheme with ```schema.sql``` file

5. run tests for a good measure
 ```python -m unittest tests```

6. set enviroments as in table below

7. uWsgi launch for dev server   ```uwsgi --socket 127.0.0.1:8000 --module wsgi --callab app --protocol http```

### Documentation provided in ```apidocs.yaml``` file. Serve it the way you like.

## ENVIROMENT VARIABLES

| Argument | Description | Example |
|:------------- |:-------------:| ------:|
| DATABASE_HOST| Postgres Host | 127.0.0.1|
| DATABASE_PORT| Postgres Port | 5423|
| DATABASE_NAME | Postgres DB name | ticket_system|
| DATABASE_TEST_NAME | Postgres test DB  name | ticket_system_test|
| DATABASE_USER| Postgres username | user|
| DATABASE_PASSWORD| Postgres password | user|
| MEMCACHE_URL| MemcahedUrl | 127.0.0.1 |
| MEMCACHE_PORT| MemcahedPort | 11211 |
| ENVIRONMENT| Connect to test or production database | test - by default|
