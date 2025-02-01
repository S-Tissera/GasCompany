import os
from flask import Flask, jsonify
from db import db  # Import db from db.py

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql+mysqlconnector://root:@localhost/gasbygas')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

    # Initialize SQLAlchemy before importing blueprints
    db.init_app(app)

    # Import and register blueprints
    from routes.auth_routes import auth_bp
    from routes.consumer_routes import consumer_blueprint
    from routes.manager_routes import manager_blueprint
    from routes.dispatch_staff import dispatch_staff_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(consumer_blueprint, url_prefix="/consumer")
    app.register_blueprint(manager_blueprint, url_prefix="/manager")
    app.register_blueprint(dispatch_staff_bp, url_prefix="/dispatch_staff")

    # Home Route
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to the Gas Management System!"})

    # Global Error Handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

    # Database Initialization
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Database initialization error: {e}")

    return app

# Run the app only when executed directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)  # Set to False in production
