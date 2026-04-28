from flask import Flask, render_template, request,flash, url_for, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy 
import os 

# Create the app and config the app with the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'reservations.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'your_secret_key'

#Create a blueprint 
reservations_bp = Blueprint('reservations', __name__)

#Create a class for reservation table
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    seat_row = db.Column(db.String(10), nullable=False)
    seat_column = db.Column(db.String(10), nullable=False)
    eticket = db.Column(db.String(100), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.id}>'

#Create a class for admin table
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Admin {self.id}>'

#Create an index route for GET and POST methods
@reservations_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form.get('menu_option')
        if option == "Reservation":
            return(redirect(url_for('reservations.reservation')))
        elif option == "Administrator":
            return(redirect(url_for('reservations.admin')))
        else:
            flash("Error: You much choose an option from the menu")
            return redirect(url_for('reservations.index'))
    
        
    return(render_template('index.html'))


    
@reservations_bp.route('/reservation')
def reservation():
    return render_template("reservation.html")

@reservations_bp.route('/admin')
def admin():
    return render_template('admin.html')

app.register_blueprint(reservations_bp)
with app.app_context():
    db.create_all()

app.run(port=5002, debug=True)