from flask import Flask, render_template, request,flash, url_for, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy
import os 

# Create the app and config the app with the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data_files', 'reservations.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'your_secret_key'

#Create a blueprint 
reservations_bp = Blueprint('reservations', __name__)

#Create a class for reservation table
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String(100), nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.String(100), unique=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Reservation {self.id}>'

#Create a class for admin table
class Admin(db.Model):
    __tablename__ = 'admins'
    username = db.Column(db.String(10), primary_key=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'

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

#Create the get_cost_matrix
def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

@reservations_bp.route('/admin', methods=['GET','POST'])
def admin():
#Create the get request that only shows the form to enter the user name and password
    if request.method == 'GET':
        return render_template('admin.html')
#Create the post request that checks if the user name and password are correct and if they are it shows the cost matrix
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:
        # Build the seating chart grid, then calculate the total sales,
        # then query all reservations and make a list of the reserved seats
            cost_matrix = get_cost_matrix()
            # Create a 12x4 grid filled with o
            occupied_seats = [[False for column in range(4)] for row in range(12)]
            reservations = Reservation.query.all()
            total_sales = 0
            for reservation in reservations:
                row = reservation.seatRow
                column = reservation.seatColumn
                total_sales += cost_matrix[row][column]
                occupied_seats[row][column] = True
            return render_template('admin.html', cost_matrix=cost_matrix, total_sales=total_sales, reservations=reservations, occupied_seats=occupied_seats)
        else:
            flash("Error: Invalid username or password")
            return redirect(url_for('reservations.admin'))

    return render_template('admin.html')

#Create a route that takes the reservation id and allows the admin to delete the reservation
@reservations_bp.route('/delete_reservation/<int:reservation_id>', methods=['POST'])
def delete_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        flash("Reservation deleted successfully")
    else:
        flash("Error: Reservation not found")
    return redirect(url_for('reservations.admin'))

app.register_blueprint(reservations_bp)
with app.app_context():
    db.create_all()

app.run(port=5002, debug=True)