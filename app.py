from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    login = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    middle_name = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    educational_institution = db.Column(db.String(150))
    password = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    inventories = db.relationship('UserInventory', backref='user', lazy='dynamic')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)  # Уникальное имя инвентаря
    quantity = db.Column(db.Integer)
    status = db.Column(db.String(50))

    users = db.relationship('UserInventory', backref='inventory', foreign_keys='UserInventory.inventory_id', lazy='dynamic')

class UserInventory(db.Model):
    __tablename__ = 'user_inventory'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
    quantity = db.Column(db.Integer)

    # Импортируем inventory_name и condition из модели Inventory
    inventory_name = db.Column(db.String(150), db.ForeignKey('inventory.name'), nullable=False)
    condition = db.Column(db.String(50), db.ForeignKey('inventory.status'), nullable=False)

class PurchasePlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150))
    supplier = db.Column(db.String(150))
    price = db.Column(db.Float)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150))
    quantity = db.Column(db.Integer)
    approved = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='requests')
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    inventory_item = db.relationship('Inventory', backref='requests')


class RepairRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150))
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def main_page():
    return redirect(url_for('user'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user_by_email = User.query.filter_by(email=identifier).first()
        user_by_login = User.query.filter_by(login=identifier).first()

        user = user_by_email or user_by_login

        if not user or not check_password_hash(user.password, password):
            flash('Неверный email/логин или пароль')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        return redirect(url_for('user'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        login = request.form.get('login')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        phone = request.form.get('phone')
        educational_institution = request.form.get('educational_institution')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash('Пароли не совпадают')
            return redirect(url_for('register'))

        user_by_email = User.query.filter_by(email=email).first()
        user_by_login = User.query.filter_by(login=login).first()

        if user_by_email or user_by_login:
            flash('Этот email или логин уже зарегистрирован')
            return redirect(url_for('register'))

        new_user = User(
            email=email,
            login=login,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            educational_institution=educational_institution,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():    
    if request.method == 'POST':
        if 'add_item' in request.form:
            name = request.form.get('name')
            quantity = int(request.form.get('quantity'))
            status = request.form.get('status')
            new_item = Inventory(name=name, quantity=quantity, status=status)
            db.session.add(new_item)
            db.session.commit()
        
        if 'add_plan' in request.form:
            item_name = request.form.get('item_name')
            supplier = request.form.get('supplier')
            price = float(request.form.get('price'))
            new_purchase = PurchasePlan(item_name=item_name, supplier=supplier, price=price)
            db.session.add(new_purchase)
            db.session.commit()
        
        if 'approve_request' in request.form:
            request_id = int(request.form.get('request_id'))
            selected_request = Request.query.get(request_id)
            inventory_name = Inventory.query.filter_by(id=selected_request.inventory_item.id).first().name
            inventory_condition = Inventory.query.filter_by(id=selected_request.inventory_item.id).first().status
            if selected_request.inventory_item.quantity >= selected_request.quantity:
                selected_request.approved = True
                selected_request.inventory_item.quantity -= selected_request.quantity

                # Добавляем инвентарь пользователю
                user_inventory_entry = UserInventory.query.filter_by(user_id=selected_request.user.id, inventory_id=selected_request.inventory_item.id).first()
                if user_inventory_entry:
                    user_inventory_entry.quantity += selected_request.quantity
                else:
                    user_inventory_entry = UserInventory(user_id=selected_request.user.id, 
                                                         inventory_id=selected_request.inventory_item.id, 
                                                         quantity=selected_request.quantity,
                                                         condition=inventory_condition,
                                                         inventory_name=inventory_name)
                    db.session.add(user_inventory_entry)

                db.session.commit()
            else:
                flash('Недостаточно инвентаря для выполнения этой заявки.')
        
        if 'reject_request' in request.form:
            request_id = int(request.form.get('request_id'))
            selected_request = Request.query.get(request_id)
            selected_request.approved = -1
            db.session.commit()

        if 'approve_repair_request' in request.form:
            repair_request_id = int(request.form.get('repair_request_id'))
            selected_repair_request = RepairRequest.query.get(repair_request_id)
            selected_repair_request.status = 'Approved'
            db.session.commit()
        
        if 'reject_repair_request' in request.form:
            repair_request_id = int(request.form.get('repair_request_id'))
            selected_repair_request = RepairRequest.query.get(repair_request_id)
            selected_repair_request.status = 'Rejected'
            db.session.commit()

        if 'change_item' in request.form:
            item_name = request.form.get('item_name')
            item_to_change = Inventory.query.filter_by(name = item_name).first()
            new_name = request.form.get('name')
            new_quantity = int(request.form.get('quantity'))
            new_condition = request.form.get('condition')
            item_to_change.name = new_name
            item_to_change.quantity = new_quantity
            item_to_change.condition = new_condition
            db.session.commit()

        if "Back_button" in request.form:
            return redirect(url_for('user'))

    inventory_items = Inventory.query.all()
    inventory_items_name = []
    for i in inventory_items:
        inventory_items_name.append(i.name)
    purchase_plans = PurchasePlan.query.all()
    requests = Request.query.all()
    repair_requests = RepairRequest.query.all()
    return render_template('admin.html', 
                           inventory_items=inventory_items, 
                           purchase_plans=purchase_plans, 
                           requests=requests, 
                           repair_requests=repair_requests, 
                           inventory_items_name=inventory_items_name)

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if request.method == 'POST':
        if 'create_repair_request' in request.form:
            item_name = request.form.get('item_name')
            description = request.form.get('description')
            new_repair_request = RepairRequest(item_name=item_name, description=description, user_id=current_user.id)
            db.session.add(new_repair_request)
            db.session.commit()
            flash('Заявка на ремонт успешно создана!')
            return redirect(url_for('user'))
    
        if 'request' in request.form:
            item_name = request.form.get('item_name')
            quantity = request.form.get('quantity_inventory')
            quantity = int(quantity)
            inventory_item = Inventory.query.filter_by(name=item_name).first()
            if inventory_item:
                new_request = Request(item_name=item_name, quantity=quantity, user=current_user, inventory_item=inventory_item)
                db.session.add(new_request)
                db.session.commit()
                flash('Заявка успешно создана!')
                print(1)
                return redirect(url_for('user'))
            else:
                flash('Инвентарь не найден')

        if 'logout' in request.form:
            return redirect(url_for('logout'))
        
        if 'AdminPanel' in request.form:
            if current_user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('user'))

    inventory_items = Inventory.query.all()
    inventory_items_name = []
    for i in inventory_items:
        inventory_items_name.append(i.name)
    repair_requests = RepairRequest.query.filter_by(user_id=current_user.id).all()
    user_inventory = UserInventory.query.filter_by(user_id = current_user.id)
    requests = Request.query.filter_by(user_id=current_user.id)
    
    return render_template('user.html', 
                           inventory_items=inventory_items, 
                           repair_requests=repair_requests, 
                           inventory_items_name = inventory_items_name,
                           user_inventory=user_inventory,
                           requests=requests)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8888)