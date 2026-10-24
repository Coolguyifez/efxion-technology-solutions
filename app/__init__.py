from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config


db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

login_manager.login_view = "admin.login"

login_manager.login_message = (
    "Please log in to access the admin area."
)

login_manager.login_message_category = (
    "warning"
)


# =========================================================
# SQLITE CONFIGURATION
# =========================================================

@event.listens_for(
    Engine,
    "connect"
)
def set_sqlite_pragma(
    dbapi_connection,
    connection_record
):

    module_name = (
        dbapi_connection
        .__class__
        .__module__
    )

    if "sqlite3" not in module_name:
        return

    cursor = dbapi_connection.cursor()

    cursor.execute(
        "PRAGMA journal_mode=WAL;"
    )

    cursor.execute(
        "PRAGMA busy_timeout=30000;"
    )

    cursor.execute(
        "PRAGMA foreign_keys=ON;"
    )

    cursor.close()


# =========================================================
# APPLICATION FACTORY
# =========================================================

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    app.config["UPLOAD_FOLDER"].mkdir(
        parents=True,
        exist_ok=True
    )

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    login_manager.init_app(app)

    from app import models

    from app.models import AdminUser

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            AdminUser,
            int(user_id)
        )

    from app.routes.main import main_bp

    app.register_blueprint(
        main_bp
    )

    from app.routes.admin import admin_bp

    app.register_blueprint(
        admin_bp
    )

    return app