from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'gagagoagjdfijgodrngoiaerhgfioaerhjgpiag')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sport_items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Items(db.Model):
    __tablename__ = 'Товары'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(100), nullable=False)

    def __init__(self, name, quantity, condition):
        self.name = name
        self.quantity = quantity
        self.condition = condition

class User(db.Model):
    __tablename__ = 'Пользователи'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024), nullable=False)
    admin = db.Column(db.Boolean, default=True)

    def __init__(self, name, surname, login, phone, email, password_hash):
        self.name = name
        self.surname = surname
        self.login = login
        self.phone = phone
        self.email = email
        self.password_hash = password_hash

class Applications(db.Model):
    __tablename__ = 'Заявки'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default="Новая")
    date = db.Column(db.Date, default = datetime.datetime.now())
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, item_id, quantity):
        self.item_id = item_id
        self.quantity = quantity

class Equipment(db.Model):
    __tablename__ = 'Оборудование'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(100), nullable=False)

    def __init__(self, name, quantity, condition):
        self.name = name
        self.quantity = quantity
        self.condition = condition

@app.route("/")
def index():
    return redirect(url_for('enter'))

@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        login = request.form.get('login')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        new_user = User(name=name, surname=surname, login=login,
                        phone=phone, email=email, password_hash=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            db.session.flush()
            return redirect(url_for("enter"))
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            return render_template("registration.html")

    return render_template("registration.html")

@app.route("/login", methods=['GET', 'POST'])
def enter():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if not login or not password:
            flash("Login and password are required.", "error")
            return render_template("enter.html")

        if login == 'admin' and password == 'admin':
            return render_template("admin.html")
        
        user = User.query.filter_by(login=login).first()
        
        if user and check_password_hash(user.password_hash, password):
            flash("Login successful!", "success")
            return redirect(url_for("main_page"))
        else:
            flash("Invalid login or password.", "error")

    return render_template("enter.html")

@app.route("/main", methods=['GET', 'POST'])
def main_page():
    items = Items.query.all()

    if request.method == 'POST':
        item_ids = request.form.getlist('item_ids')
        quantity = request.form.get('quantity')

        if not item_ids or not quantity:
            flash('Please select items and specify the quantity.', 'error')
            return render_template("main.html", items=items)

        user_id = session.get('user_id')  # Retrieve user ID from the session
        for item_id in item_ids:
            new_application = Applications(item_id=item_id, quantity=quantity)
            db.session.add(new_application)

        db.session.commit()
        flash('Request submitted successfully!', 'success')

    return render_template("main.html", items=items)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
    finally:
        db.session.close()

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    items = Items.query.all()

    if request.method == 'POST':
        # Check if the request is for adding a new item
        if 'name' in request.form:
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            condition = request.form.get('condition')

            new_item = Items(name=name, quantity=quantity, condition=condition)
            db.session.add(new_item)
            db.session.commit()
            flash('New item added successfully!', 'success')

        # Check if the request is for changing an existing item
        elif 'item_id' in request.form:
            item_id = int(request.form.get('item_id'))
            item = Items.query.get(item_id)

            if item:
                new_quantity = request.form.get('new_quantity')
                new_condition = request.form.get('new_condition')

                item.quantity = new_quantity
                item.condition = new_condition
                db.session.commit()
                flash('Item updated successfully!', 'success')

        # Check if it's processing an application
        elif 'application_id' in request.form:
            action = request.form.get('action')
            application_id = int(request.form.get('application_id'))
            application = Applications.query.get(application_id)

            if action == 'accept':
                # Update the application status, reduce the item quantity, and delete the application
                item = Items.query.get(application.item_id)
                item.quantity -= application.quantity
                application.status = 'Принята'
                db.session.delete(application)
                db.session.commit()
                flash('Application accepted successfully!', 'success')

            elif action == 'reject':
                # Update the application status and delete the application
                application.status = 'Отклонена'
                db.session.delete(application)
                db.session.commit()
                flash('Application rejected successfully!', 'success')

    applications = Applications.query.all()  # Fetch applications again after POST

    return render_template("admin.html", applications=applications, items=items)



@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
    finally:
        db.session.close()

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)

        db.create_all()

    app.run(port=8080, host='127.0.0.1', debug=True)