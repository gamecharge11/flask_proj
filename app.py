from flask import Flask, url_for, redirect, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
 
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    place = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20),nullable=False)
    crops = db.Column(db.String(200))
    model = db.Column(db.String(50))
    deliveries = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
@app.route("/", methods=["POST","GET"])
def index():
    if request.method == "POST":
        resp = make_response(redirect("/"))
        resp.set_cookie("token","None",max_age=0)
        return resp

    if request.cookies.get("token") is not None:
        user = User.query.filter_by(uid=request.cookies.get("token")).first()
        users = User.query.all()
        return render_template("index.html", user=user, users=users)
    else:
        return redirect("/register")
    
@app.route("/register", methods=["POST","GET"])
def register():
    if request.cookies.get("token") is not None:
        return redirect("/")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        phone = request.form["phone"]
        place = request.form["place"]
        mod = request.form["model"]
        print(place)
        type = request.form['type']
        crops = ""
        if type == "farmer":
            crops = "[]"
        else:
            crops = "NA"

        model = ""
        if type == "trucker":
            model=mod
        else:
            model="NA"

        deliveries = ""
        if type == "trucker":
            deliveries = 0
        else:
            deliveries = -1
        if len(User.query.filter_by(username=username).all()) == 0:
            uid = str(uuid4())
            user = User(username = username, password = password,uid=uid, type=type, phone=phone, place=place, crops=crops, model=model, deliveries = deliveries)

            db.session.add(user)
            db.session.commit()

            resp = make_response(redirect("/"))
            resp.set_cookie("token",uid,max_age=864000)

            return resp
        else:
            return "Username in use"

    return render_template("create.html")

@app.route("/login",methods=["POST","GET"])
def login():
    if request.cookies.get("token") is not None:
        return redirect("/")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        attemptedUser = User.query.filter_by(username=username).first()
        if attemptedUser is not None:
            if attemptedUser.password == password:
                resp = make_response(redirect("/"))
                resp.set_cookie("token",attemptedUser.uid,max_age=864000)
                return resp
            
    return render_template("login.html")

@app.route("/crops", methods=["POST","GET"])
def crops():
    if request.method == "POST":
        if request.form['add'] is not None:
            crop = request.form['crop']
            farmer = User.query.filter_by(uid=request.cookies.get("token")).first()
            crops = json.loads(farmer.crops)
            crops.append(crop)
            x = json.dumps(crops)
            farmer.crops = x
            db.session.commit()
            return redirect("crops")
        # if request.form['delete'] is not None:
        #     crop = request.form['number']
        #     farmer = User.query.filter_by(uid=request.cookies.get("token")).first()
        #     crops = json.loads(farmer.crops)
        #     crops.pop(int(crop))
        #     farmer.crops = json.dumps(crops)
        #     db.session.commit()
        #     return redirect("crops")
        else:
            return ""
    else:
        if request.cookies.get("token") is not None:
            user = User.query.filter_by(uid=request.cookies.get("token")).first()
            crops = json.loads(user.crops)
            return render_template("crops.html",crops=crops)
        else:
            return redirect("/")
        
@app.route("/delete-<int:i>",methods=["GET"])
def delete(i):
    if request.method == "GET":
        crop = i
        farmer = User.query.filter_by(uid=request.cookies.get("token")).first()
        crops = json.loads(farmer.crops)
        crops.pop(int(crop))
        farmer.crops = json.dumps(crops)
        db.session.commit()
        return redirect("crops")
    
@app.route('/truckers',methods=["POST","GET"])
def truckers():
    if request.method == "POST":
        pass
    truckers = User.query.filter_by(type="trucker").all()
    return render_template("truckers.html", truckers=truckers)

if __name__ == "__main__":
    app.run(debug=True)