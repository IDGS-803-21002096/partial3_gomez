from flask import Flask, render_template, request, redirect, url_for
from flask import session
from flask_login import LoginManager
from flask_login import login_user, login_required, current_user
from flask_login import logout_user
from werkzeug.security import check_password_hash
from flask import flash
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from flask import g
import forms
from datetime import datetime, date

from models import db
from models import Pedido
from models import Usuario

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    session.pop('_flashes', None)
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Usuario.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'success')
    session.pop('_flashes', None)
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    create_form = forms.UserForm()

    registros = []
    try:
        with open("registros.txt", "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(",")

                if len(datos) >= 8:
                    tamaño = datos[3]
                    ingredientes = ",".join(datos[4:-3])
                    try:
                        cantidadPizzas = int(datos[-3])
                        subtotal = float(datos[-2])
                    except ValueError:
                        cantidadPizzas = 0
                        subtotal = 0.0

                    registros.append({
                        "tamaño": tamaño,
                        "ingredientes": ingredientes,
                        "cantidadPizzas": cantidadPizzas,
                        "subtotal": subtotal
                    })
    except FileNotFoundError:
        registros = []
    
    return render_template("index.html", form=create_form, registros=registros)

@app.route("/save", methods=["GET", "POST"])
@login_required
def save():
    create_form = forms.UserForm(request.form)
    
    if request.method == "POST":
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        tamaño = request.form.get("tamaño")
        ingredientes = request.form.getlist("ingredientes")
        cantidadPizzas = int(request.form.get("cantidadPizzas", 0))

        # Precios
        precios_tamaño = {
            "chica": 40,
            "mediana": 80,
            "grande": 120
        }
        precio_ingrediente = 10

        # Calcular subtotal
        precio_tamaño = precios_tamaño.get(tamaño, 0)
        precio_ingredientes = len(ingredientes) * precio_ingrediente
        subtotal = (precio_tamaño + precio_ingredientes) * cantidadPizzas

        with open("registros.txt", "a") as archivo:
            archivo.write(f"{nombre},{direccion},{telefono},{tamaño},{','.join(ingredientes)},{cantidadPizzas},{subtotal},{datetime.utcnow().date()}\n")
        
        return redirect(url_for("index"))

    return render_template("index.html", form=create_form)

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    id_registro = int(request.form.get("id", 0))

    if id_registro:
        with open("registros.txt", "r") as archivo:
            registros = archivo.readlines()
        
        # Eliminar el registro basado en la línea correspondiente
        if 0 < id_registro <= len(registros):
            del registros[id_registro - 1]
        
        # Sobrescribir el archivo con los registros restantes
        with open("registros.txt", "w") as archivo:
            archivo.writelines(registros)

    return redirect(url_for("index"))

@app.route("/cargar_pedidos", methods=["POST"])
@login_required
def cargar_pedidos():
    try:
        with open("registros.txt", "r") as file:
            lineas = file.readlines()

        for linea in lineas:
            datos = linea.strip().split(',')

            if len(datos) >= 8:
                nombre, direccion, telefono, tamaño, *ingredientes, num_pizzas, subtotal, fecha = datos
                ingredientes = ",".join(ingredientes)  # Une los ingredientes separados por coma
                
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

                # Crear el objeto y guardarlo en la base de datos
                pedido = Pedido(
                    nombre=nombre,
                    direccion=direccion,
                    telefono=telefono,
                    tamaño=tamaño,
                    ingredientes=ingredientes,
                    num_pizzas=int(num_pizzas),
                    subtotal=float(subtotal),
                    fecha=fecha
                )
                db.session.add(pedido)  # Añadir a la sesión

        db.session.commit()  # Guardar en la base de datos
        
        with open("registros.txt", "w") as file:
            file.write("")

        flash("Registros guardados correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar registros: {str(e)}", "danger")
    
    return redirect(url_for("index"))

@app.route("/ventas_totales", methods=["POST"])
@login_required
def ventas_totales():
    create_form = forms.UserForm(request.form)

    try:
        hoy = date.today()
        pedidos = Pedido.query.filter(db.func.date(Pedido.fecha) == hoy).all()

        total = sum(pedido.subtotal for pedido in pedidos)

        mensaje_ventas = f"${total:.2f}" if total > 0 else "$0.00"
        return render_template("index.html", form=create_form, pedidos=pedidos, ventas_totales=mensaje_ventas, mensaje_error=None)
    
    except Exception as e:
        mensaje_error = f"Error al obtener ventas totales: {str(e)}"
        return render_template("index.html", form=create_form, pedidos=[], ventas_totales="$0.00", mensaje_error=mensaje_error)

if __name__ == '__main__':
	csrf.init_app(app)
	db.init_app(app)

	with app.app_context():
		db.create_all()
	app.run()