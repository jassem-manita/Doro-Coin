from flask import *
from wtforms import *
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
from flaskfuncs import *
import time


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# wrap to define if the user is currently logged in from session


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login.", "danger")
            return redirect(url_for('login'))
    return wrap

# user login


def log_in_user(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')


# registration page
class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(
    ), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    # collect data if form is submitted
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        name = form.name.data

        # if user doesn't exist add it to mysql and log in
        if isnewuser(username):
            password = sha256_crypt.encrypt(form.password.data)
            users.insert(name, email, username, password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)


# login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    # collect from data if form is submitted
    if request.method == 'POST':
        username = request.form['username']
        candidate = request.form['password']
        users = Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        accPass = user.get('password')

        # if the password cannot be found the user doesn't exist than you may be need to get the duck outta here
        if accPass is None:
            flash("Username is not found", 'danger')
            return redirect(url_for('login'))
        else:
            # if the entered password matches the actual password log in the user's dashboard page and earn some coins
            if sha256_crypt.verify(candidate, accPass):
                log_in_user(username)
                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                # if the passwords doesn't match
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


# transaction page
class SendMoneyForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    amount = StringField('Amount', [validators.Length(min=1, max=50)])


@app.route("/transaction", methods=['GET', 'POST'])
@is_logged_in
def transaction():
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))

    # if form is submitted
    if request.method == 'POST':
        try:
            # execute the transaction
            send_money(session.get('username'),
                       form.username.data, form.amount.data)
            flash("Money Sent!", "success")
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('transaction'))

    return render_template('transaction.html', balance=balance, form=form, page='transaction')


# buy page
class BuyForm(Form):
    amount = StringField('Amount', [validators.Length(min=1, max=50)])


@app.route("/buy", methods=['GET', 'POST'])
@is_logged_in
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))
    if request.method == 'POST':
        try:
            send_money("BANK", session.get('username'), form.amount.data)
            flash("Purchase Successful!", "success")
        except Exception as e:
            flash(str(e), 'danger')

        return redirect(url_for('dashboard'))

    return render_template('buy.html', balance=balance, form=form, page='buy')


# logout the user
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("Logout success", "success")
    return redirect(url_for('login'))


# dashboard page
@app.route("/dashboard")
@is_logged_in
def dashboard():
    balance = get_balance(session.get('username'))
    blockchain = get_blockchain().chain
    ct = time.strftime("%I:%M %p")
    return render_template('dashboard.html', balance=balance, session=session, ct=ct, blockchain=blockchain, page='dashboard')


# index page
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


# run app
if __name__ == '__main__':
    app.secret_key = 'jawher_y7b_faten_w_faten_t7b_aziz_w_aziz_y7b_moune'
    app.run(debug=True)
