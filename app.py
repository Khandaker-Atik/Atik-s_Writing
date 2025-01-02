from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import datetime

# Initialize the Flask app and load configuration
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# This function loads a user given the user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Import routes after initializing the app and extensions
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
