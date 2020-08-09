#!/bin/bash

# start mysql container
docker run -d -p 3306:3306 --name=mysql_container -e MYSQL_ROOT_PASSWORD=abcd1234 mysql

# start flask container
docker run -d --network=host -v $PWD:/app flask_imdb python3 app.py
