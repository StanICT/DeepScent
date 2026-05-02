from flask import Flask, render_template
from flask_login import LoginManager
from .extensions import db, migrate   # import from extensions

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initialize db and migrate
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from .models import User, Product   # import models AFTER db is ready
        db.create_all()

    # login manager setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # register blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    # error handler for forbidden access
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    return app
