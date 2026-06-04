from flask import Flask, jsonify
from flask_cors import CORS

from app.blueprints.admin import admin_bp
from app.blueprints.auth import auth_bp
from app.blueprints.parking import parking_bp
from app.blueprints.reservations import reservations_bp
from app.config import Config
from app.database import init_db
from app.errors import ApiError


def create_app(config_override: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    if not app.config.get("TESTING"):
        init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(parking_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify({"detail": error.message}), error.status_code

    @app.get("/health")
    def health_check():
        return jsonify({"status": "healthy", "service": Config.APP_NAME, "version": Config.APP_VERSION})

    @app.get("/")
    def root():
        return jsonify(
            {
                "message": "Welcome to ParkSmart API",
                "health": "/health",
                "api": "/api/v1",
            }
        )

    return app
