from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

db=SQLAlchemy()
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(150))
    telefono = db.Column(db.String(20))
    tamaño = db.Column(db.String(20))
    ingredientes = db.Column(db.String(200))
    num_pizzas = db.Column(db.Integer)
    subtotal = db.Column(db.Float)
    fecha = db.Column(db.Date, default=datetime.utcnow)

class Usuario(db.Model, UserMixin):
    __tablename__='usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Función para hashear la contraseña
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Función para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.password, password)

