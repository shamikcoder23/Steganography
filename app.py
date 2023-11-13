import cv2
import os
import string
from flask import Flask, render_template, request, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(250), unique=True, nullable=False)
	password = db.Column(db.String(250), nullable=False)
	message = db.Column(db.String(250))

db.init_app(app)

with app.app_context():
	db.create_all()

@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)

@app.route('/register', methods=["GET", "POST"])
def register():
	if request.method == "POST":
		user = Users(username=request.form.get("username"),
					password=request.form.get("password"),
					message="")
		db.session.add(user)
		db.session.commit()
		return redirect(url_for("login"))
	return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		user = Users.query.filter_by(username=request.form.get("username")).first()
		if user.password == request.form.get("password"):
			login_user(user)
			return redirect(url_for("home"))
		else:
			return redirect(url_for("register"))
	return render_template("login.html")

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("login"))

d = {}
c = {}
for i in range(255):     # 0 to 254 ie 255 bits of character to be used
	d[chr(i)] = i
	c[i] = chr(i)
msg = ""
img = []

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == "POST":
		msg = request.form.get("msg")
		user = Users.query.filter_by(username=request.form.get("username")).first()
		user.message = msg
		db.session.commit()
		img = cv2.imread("static/Steg.png")

		m = 0     # decides no of columns
		n = 0     # decides no of rows
		z = 0     # decides pixel plane
		for _ in range(3):
			for i in range(len(msg)):
				img[n,m,z] = d[msg[i]]
				n += 1
				m += 1
				z = (z+1) % 3
		cv2.imwrite("static/Encrypt_new.png", img)
		return redirect(url_for("message"))
	return render_template("home.html")

@app.route("/stego", methods=["GET", "POST"])
def message():
	if request.method == "POST":
		user = Users.query.filter_by(username=request.form.get("username")).first()
		if user.password == request.form.get("password"):
			print("Encrypted message : ", user.message)
			return render_template("message.html", res=user.message)
		else:
			return redirect(url_for("register"))
	return render_template("message.html")

if __name__ == "__main__":
	app.run(debug=True)
