
#!/usr/bin/python

from flask import Flask, render_template, make_response, redirect
from flask import request
import sys
import time

import db_interact

'''
Backend for IMDB, serving API's
'''

app = Flask(__name__)

@app.route("/auth",methods=['POST'])
def auth():
    '''
    Function for handling authentication of the user.
    '''
    try:
        if ("username" not in request.form or \
                "password" not in request.form):
            return redirect("/",code=302)

        user_name = request.form['username']
        password = request.form['password']

        # Verify user creds from DB query
        validated = db_interact.validate_user(user_name, password)
        if (validated and validated[0]):
            print ("{} : {}, is_admin:{}".format(user_name, password, validated[1]))
            if (validated[1]):
                resp = make_response(render_template('admin_home.html', 
                        movies_list=db_interact.get_all_movies()))
                resp.set_cookie('auth_type', 'admin', max_age=60*60) # 1hour
                return resp
            else:
                resp = make_response(render_template('user_home.html', 
                        movies_list=db_interact.get_all_movies()))
                resp.set_cookie('auth_type', 'user', max_age=60*60) # 1hour
                return resp
        return render_template('unauthorized.html')
    except Exception as e:
        print ("[#] Error: auth(): ", e)
        return redirect("/",code=302)

@app.route("/search_page",methods=['POST'])
def search_page():
    '''
    For Rendering the search page
    '''
    try:
        keyword = "" 
        if "search_query" in request.form:
            keyword = request.form['search_query']
        keyword_movies = db_interact.search(keyword)

        cookie_value = request.cookies.get('auth_type')
        if (cookie_value == ""):
            return render_template('index.html')
        elif (cookie_value == 'admin'):
            return render_template('admin_home.html', movies_list = keyword_movies)
        elif (cookie_value == 'user'):
            return render_template('user_home.html', movies_list = keyword_movies)
        else:
            return redirect("./logout", code=302)
    except Exception as e:
        print ("[#] Error: search_page(): ",e)
        return render_template('index.html')


@app.route('/update_movie')
def update_movie():
    '''
    This route returns the webpage for adding
    movie in the Database.
    '''
    try:
        cookie_value = request.cookies.get("auth_type")
        # only admin can add new movies
        if (cookie_value != "admin"):
            return redirect("/",code=302)
        return render_template("update_movie.html")
    except Exception as e:
        print ("[#] Error: update_movie(): " ,e)
        return redirect("/",code=302)

@app.route('/update',methods=['POST'])
def update():
    '''
    This function updates movie to the database.
    '''
    try:
        cookie_value = request.cookies.get("auth_type")
        # only admin can add new movies
        if (cookie_value != "admin"):
            return redirect("/",code=302)

        parameters = ["imdb_score", "popularity", "director_name", "genre", "movie_name"]
        movie_details = []
        for param in parameters:
            if param not in request.form:
                return "<h3> {} field cannot be empty </h3>".format(param)
            else:
                movie_details.append( request.form[param] )

        if not (db_interact.update_movie(movie_details)):
            return "<h3> Unable to update Movie details for {}".\
                    format(movie_details[-1])

        return redirect("/update_movie",code=302)
    except Exception as e:
        print ("[#] Error: update_movie(): " ,e)
        return redirect("/",code=302)

@app.route('/remove_movie')
def remove_movie():
    '''
    This route returns the webpage for removing
    movies from the Database.
    '''
    try:
        cookie_value = request.cookies.get("auth_type")
        # only admin can remove movies
        if (cookie_value != "admin"):
            return redirect("/",code=302)
        return render_template("remove_movie.html")
    except Exception as e:
        print ("[#] Error: update_movie(): " ,e)
        return redirect("/",code=302)

@app.route('/remove',methods=['POST'])
def add():
    '''
    This function removes the movie from the database.
    '''
    try:
        cookie_value = request.cookies.get("auth_type")
        # only admin can add new movies
        if (cookie_value != "admin"):
            return redirect("/",code=302)
        
        if "movie_name" not in request.form:
            return "<h3> Movie_name field cannot be empty </h3>"
        
        movie_name = request.form['movie_name']
        if not (db_interact.remove_movie(movie_name)):
            return "<h3> Unable to remove Movie details for {}".\
                    format(movie_name)

        return redirect("/",code=302)
    except Exception as e:
        print ("[#] Error: update_movie(): " ,e)
        return redirect("/",code=302)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    '''
    Return to index page for all undefined routes.
    '''
    return redirect("./", code=302)

@app.route('/logout')
def logout():
    '''
    This function logs out the current user.
    '''
    # Set cookie to empty
    try:
        resp = make_response(render_template('index.html'))
        resp.set_cookie('auth_type', '', max_age=60*60) # 1hour
        return resp
    except Exception as e:
        print ("[#] Error: update_movie(): " ,e)
        return redirect("/",code=302)

@app.route("/")
def index():
    '''
    Render the index/login page for the webapp.
    '''
    try:
        cookie_value = request.cookies.get('auth_type')
        if (cookie_value == ""):
            return render_template('index.html')

        elif (cookie_value == 'admin'):
            return render_template('admin_home.html', movies_list = db_interact.get_all_movies())
        elif (cookie_value == 'user'):
            return render_template('user_home.html', movies_list = db_interact.get_all_movies())
        else:
            return redirect("./logout", code=302)
    except Exception as e:
        print ("[#] Error: update_movie(): " ,e)
        return "<h3>503: For maintenance purposes server is currently down,\
                please try again later </h3>"

if __name__ == "__main__":
    if not (db_interact.connect_db(app)):
        print ("[#] Unable to initiate connection with Database")
        sys.exit(1)
    app.run(debug=True)
