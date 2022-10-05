import datetime

import bcrypt
import pymongo
from flask import Flask, jsonify, redirect, request, session, url_for,render_template
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required)

app = Flask(__name__)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "42hscnbw468tymdrte6y3r1235efww21yy6sf"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
app.config["PROPAGATE_EXCEPTIONS"] = True

app.secret_key = "task"
client = pymongo.MongoClient(
    "mongodb+srv://task:sarim123@cluster0.rjskfy3.mongodb.net/?retryWrites=true&w=majority"
)
db = client.get_database("records")
records = db.register
templates = db.template


@app.route("/", methods=["GET"])
def home():
    return render_template('home.html', content="Hello World!")


@app.route("/register", methods=["post"])
def register():
    message = ""
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        f_user = request.form.get("first_name")
        l_user = request.form.get("last_name")
        user = f"{f_user} {l_user}"
        email = request.form.get("email")

        password = request.form.get("password")

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = "There already is a user by that name"
            return message
        if email_found:
            message = "This email already exists in database"
            return message
        else:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user_input = {"name": user, "email": email, "password": hashed}
            records.insert_one(user_input)

            user_data = records.find_one({"email": email})
            new_email = user_data["email"]

            return "User created successfully"
    return message


@app.route("/logged_in")
def logged_in():
    if "email" not in session:
        return "You are not logged in"
    email = session["email"]
    return {"Result": f"Welcome {email}"}


@app.route("/login", methods=["POST"])
def login():
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not (email_found := records.find_one({"email": email})):
            return jsonify({"msg": "The username or password is incorrect"}), 401
        email_val = email_found["email"]
        passwordcheck = email_found["password"]

        if bcrypt.checkpw(password.encode("utf-8"), passwordcheck):
            session["email"] = email_val
            access_token = create_access_token(identity=email_found["email"])
            return jsonify(access_token=access_token), 200
        else:
            if "email" in session:
                return redirect(url_for("logged_in"))
            return jsonify({"msg": "The username or password is incorrect"}), 401
    return jsonify({"msg": "The username or password is incorrect"}), 401


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" not in session:
        return "You are not logged in"
    email = session["email"]
    session.pop("email", None)
    return f"logged out {email}"


@app.route("/template", methods=["POST", "GET", "PUT", "DELETE"])
@jwt_required()
def template():
    current_user = get_jwt_identity()
    if not (user_from_db := records.find_one({"email": current_user})):
        return jsonify({"msg": "Profile not found"}), 404
    del user_from_db["_id"], user_from_db["password"]
    if request.method not in ["POST", "GET", "PUT", "DELETE"]:
        return "Method not allowed"
    if request.method == "POST":
        template_name = request.form["template_name"]
        subject = request.form["subject"]
        body = request.form["body"]
        templates.insert_one(
            {"template_name": template_name, "subject": subject, "body": body}
        )
        return "Template created successfully"
    elif request.method == "PUT":
        template_name = request.form["template_name"]
        if not template_name:
            return "Please fill all the fields"
        find_one = {"template_name": template_name}
        update_this = {
            "$set": {
                "template_name": request.form["new_template"],
                "subject": request.form["new_subject"],
                "body": request.form["new_body"],
            }
        }
        templates.update_one(find_one, update_this)
        return "Template updated successfully"
    elif request.method == "DELETE":
        template_name = request.form["template_name"]
        templates.delete_one({"template_name": template_name})
        return "Template deleted successfully"
    elif request.method == "GET":
        if template_name := templates.find_one(
            {
                "template_name": request.form["template_name"],
            }
        ):
            return template_name["template_name"]
        temps = templates.find({"template_name": request.form["template_name"]})
        return [temp.get("template_name") for temp in temps]


# end of code to run it
if __name__ == "__main__":
    app.run(debug=True, port=5000)
