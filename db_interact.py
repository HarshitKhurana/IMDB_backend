
#!/usr/bin/python

from flask import Flask
from flaskext.mysql import MySQL

'''
This module handle all the DB interactions for 
webapp and returns response in specified format.

The reasone for this to be a seperate module is so
that in future if reqd it can be replaced by ORM.
Eg: SQLAlchemy
'''

mysql = MySQL()
mysql_user = "root"
mysql_pass = "abcd1234"
mysql_db_name = "Data"
mysql_db_host = "localhost"
cursor = None
mysql_conn = None


def connect_db(flask_app):
    '''
    This function connects to the MySQL database
    and creates cursort object.
    '''
    global cursor
    global mysql
    global mysql_conn
    global mysql_conn_user
    global mysql_conn_pass
    global mysql_conn_db_name
    global mysql_conn_db_host
    try:
        flask_app.config['MYSQL_DATABASE_PASSWORD'] = mysql_pass
        flask_app.config['MYSQL_DATABASE_USER'] = mysql_user
        flask_app.config['MYSQL_DATABASE_DB'] = mysql_db_name
        flask_app.config['MYSQL_DATABASE_HOST'] = mysql_db_host
        mysql.init_app(flask_app)

        mysql_conn = mysql.connect()
        cursor = mysql_conn.cursor()

        cursor.execute("SELECT * from Users")
        data = cursor.fetchone()
        mysql_conn.commit()
        return True
    except Exception as e:
        mysql_conn.rollback()
        print ("[#] Error: connect_db(): ",e)
        return False

def validate_user(user_name, password):
    '''
    This function validates the user credentials,
    and returns True if creds are valid else False.
    '''
    global cursor
    global mysql_conn
    try:
        cursor.execute("Select password,is_admin from Users where user_name='{}'".
                format(user_name))
        password_isAdmin = cursor.fetchone()
        mysql_conn.commit()
        if (password_isAdmin):
            _db_password_value = password_isAdmin[0]
            _is_admin = password_isAdmin[1]
            return (_db_password_value == password, _is_admin)
        else:   
            return (False,False)
    except Exception as e:
        mysql_conn.rollback()
        print ("[#] Error: validate_user(): ", e)
        return (False,False)

def remove_movie(movie_name):
    '''
    This function is used to remove a movie from
    the table.
    '''
    global cursor
    global mysql_conn
    try:
        # Will raise exception incase it fails
        if (movie_name):
            cursor.execute("Delete from Movies where movie_name='{}'".format(movie_name))
            mysql_conn.commit()
        return True
    except Exception as e:
        mysql_conn.rollback()
        print ("[#] Error: remove_movie(): ",e)
        return False

def update_movie(row_parameters):
    '''
    This function is used to add/update a movie in
    the Movies table.
    '''
    global mysql_conn
    global cursor
    imdb_score, popularity, director_name, genre, movie_name = row_parameters
    try:
        upsert_query = 'Insert into Movies (imdb_score, 99popularity, director_name, genre, movie_name) \
                VALUES (\"{}\", \"{}\", \"{}\",\"{}\", \"{}\") \
                ON DUPLICATE KEY UPDATE \
                imdb_score=\"{}\", 99popularity=\"{}\", director_name=\"{}\", \
                genre=\"{}\"'.format(imdb_score, popularity, director_name, genre,\
                        movie_name, imdb_score, popularity, director_name, genre)

        # Will raise exception incase it fails
        cursor.execute(upsert_query)    
        mysql_conn.commit()
        return True
    except Exception as e:
        mysql_conn.rollback()
        print ("[#] Error: update_movie(): ",e)
        return False

def get_all_movies():
    '''
    This function returns a list of all the 
    movies listed in the database.
    '''
    global mysql_conn
    global cursor
    try:
        # Will raise exception incase it fails
        cursor.execute("Select movie_name,director_name,genre,imdb_score,99popularity from Movies")
        all_movies = cursor.fetchall()
        mysql_conn.commit()
        return all_movies
    except Exception as e:
        mysql_conn.rollback()
        print ("[#] Error: get_all_movies() : ", e)
        return []

def search(keyword):
    '''
    This function returns the list of movies
    containing the keyword.
    '''
    global mysql_conn
    global cursor
    try:
        if (keyword == ""):
            return get_all_movies()
        query_string = "Select movie_name,director_name,genre,imdb_score,99popularity \
                        from Movies Where MATCH(movie_name,director_name,genre) AGAINST \
                        ('{}' IN NATURAL LANGUAGE MODE);".format(keyword)
        cursor.execute(query_string)
        relevant_rows = cursor.fetchall()
        mysql_conn.commit()
        return relevant_rows
    except Exception as e:
        mysql_conn.rollback()
        print ("[#] Error: search() : ", e)
        return []
