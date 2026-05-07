from flask import Flask, redirect, url_for
from config import TEMPLATE_DIR
from routes import *

def create_app() -> Flask:
    app = Flask(__name__, template_folder=TEMPLATE_DIR)

    # Registro de blueprints
    app.register_blueprint(alumnos_bp, name = "alumnos")
    app.register_blueprint(cursos_bp, name = "cursos")
    app.register_blueprint(home_bp, name = "home")
    app.register_blueprint(matriculas_bp, name = "matriculas")
    app.register_blueprint(profesores_bp, name = "profesores")
    app.register_blueprint(transacciones_bp, name = "transacciones")

    # Redireccionamiento
    @app.route("/")
    def index():
        return redirect(url_for('home.home'))
    
    return app