from flask import Flask
from config import Config

from models import db , setup_database



app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)

import models
import controllers.admin_routes
import controllers.user_routes
import controllers.authentication

from models import setup_database 



if __name__ == "__main__":

    with app.app_context():
        
        setup_database(app,db)
    app.run(debug=True)