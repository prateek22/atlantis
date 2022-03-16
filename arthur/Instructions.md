# Starting the cassandra server
```
# docker run -d     --name my-cassandra     -p 9042:9042     -v ~/apps/cassandra:/var/lib/cassandra     -e CASSANDRA_CLUSTER_NAME=citizix     cassandra:4.0
# docker exec -it my-cassandra /bin/bash
# cqlsh -u cassandra -p cassandra
```

# Running the django project
```
# python3 -m pip install --upgrade pip
# pip3 install Django django-cassandra-engine django-crispy-forms django-sslserver django-extensions Werkzeug passlib pyOpenSSL
# python3 manage.py makemigrations
# python3 manage.py migrate
# python3 manage.py sync_cassandra
# python3 manage.py runserver_plus --cert-file ../../certs/local.crt --key-file ../../certs/local.key.pem --reloader-interval 2 0.0.0.0:8000
```