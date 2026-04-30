from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return 'This is the login page'

@auth.route('/signup')
def signup():
    return 'This is the signup page'


