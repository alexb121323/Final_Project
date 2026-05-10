from flask import Flask, render_template, request,flash, url_for, redirect, Blueprint
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string
from datetime import datetime

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


# Added by reservations branch 

#Generate an e-ticket number by alternating characters from the first name and INFOTC4320
def generate_eticket(first_name):
    info_string = "INFOTC4320"
    eticket = ""
    for i in range(max(len(first_name), len(info_string))):
        if i < len(first_name):
            eticket += first_name[i]
        if i < len(info_string):
            eticket += info_string[i]
    return eticket

#Create the reservation route for GET and POST methods
@reservations_bp.route('/reservation', methods=['GET', 'POST'])
def reservation():
    # Build occupied seats grid to display the seating chart
    occupied_seats = [[False for column in range(4)] for row in range(12)]
    for res in Reservation.query.all():
        occupied_seats[res.seatRow][res.seatColumn] = True

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name', '').strip()
        seat_row   = request.form.get('seat_row')
        seat_column = request.form.get('seat_column')

        # Validate inputs
        if not first_name or not last_name:
            flash("Error: First and last name are required.")
            return redirect(url_for('reservations.reservation'))

        try:
            seat_row = int(seat_row)
            seat_column = int(seat_column)
        except (TypeError, ValueError):
            flash("Error: Row and column must be numbers.")
            return redirect(url_for('reservations.reservation'))

        if not (0 <= seat_row <= 11) or not (0 <= seat_column <= 3):
            flash("Error: Row must be 0-11 and column must be 0-3.")
            return redirect(url_for('reservations.reservation'))

        if occupied_seats[seat_row][seat_column]:
            flash(f"Error: Seat Row {seat_row}, Column {seat_column} is already taken. Please choose another seat.")
            return redirect(url_for('reservations.reservation'))

        # Generate a unique e-ticket number
        eticket = generate_eticket(first_name)


        # Insert the reservation into the database
        passenger_name = f"{first_name} {last_name}"
        new_reservation = Reservation(
            passengerName=passenger_name,
            seatRow=seat_row,
            seatColumn=seat_column,
            eTicketNumber=eticket,
            created=datetime.utcnow()
        )
        db.session.add(new_reservation)
        db.session.commit()

        # Show confirmation with e-ticket code
        return render_template(
            'reservation.html',
            reservation_code=eticket,
            passenger_name=passenger_name,
            seat_row=seat_row,
            seat_column=seat_column,
            occupied_seats=occupied_seats
        )

    return render_template('reservation.html', occupied_seats=occupied_seats)

# End of reservations branch additions


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
