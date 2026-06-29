# app.py
from flask import Flask
from flask_login import LoginManager
from model.models import db, User
from view.auth import auth
from view.dashboard import dashboard
from utils.config import Config



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(dashboard)

    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)