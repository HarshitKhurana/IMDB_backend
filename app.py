
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

@app.route("/search_page",methods=['POST'])
def search_page():
    '''
    For Rendering the search page
    '''
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


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    '''
    Return to index page for all undefined routes.
    '''
    print ("Request on {} redirecting request to index".format(path))
    print ("{}".format(request.cookies.get("auth_type")))
    return redirect("./", code=302)

@app.route('/logout')
def logout():
    '''
    This function logs out the current user.
    '''
    # Set cookie to empty
    resp = make_response(render_template('index.html'))
    resp.set_cookie('auth_type', '', max_age=60*60) # 1hour
    return resp

@app.route("/")
def index():
    '''
    Render the index/login page for the webapp.
    '''
    cookie_value = request.cookies.get('auth_type')
    if (cookie_value == ""):
        return render_template('index.html')

    elif (cookie_value == 'admin'):
        return render_template('admin_home.html', movies_list = db_interact.get_all_movies())
    elif (cookie_value == 'user'):
        return render_template('user_home.html', movies_list = db_interact.get_all_movies())
    else:
        return redirect("./logout", code=302)

if __name__ == "__main__":
    if not (db_interact.connect_db(app)):
        print ("[#] Unable to initiate connection with Database")
        sys.exit(1)
    app.run(debug=True)
