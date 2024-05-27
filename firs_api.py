from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "secret_key"
app.config["MONGO_URI"] = "mongodb://localhost:27017/users"
mongo = PyMongo(app)


@app.route("/add", methods=["POST"])
def add_user():
    _json = request.json
    _name = _json["name"]
    _email = _json["email"]
    _password = _json["password"]

    if _name and _email and _password and request.method == "POST":
        _hashed_password = generate_password_hash(_password)
        id = mongo.db.user.insert_one(
            {"name": _name, "email": _email, "password": _hashed_password}
        )
        resp = jsonify("User added successfully!")
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route("/delete/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        mongo.db.user.delete_one({"_id": ObjectId(id)})
        resp = jsonify("User deleted successfully!")
        resp.status_code = 200
        return resp
    except Exception as e:
        return not_found()


@app.route("/update/<id>", methods=["PUT"])
def update_user(id):
    _json = request.json
    _name = _json["name"]
    _email = _json["email"]
    _password = _json["password"]

    if _name and _email and _password and request.method == "PUT":
        _hashed_password = generate_password_hash(_password)
        mongo.db.user.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": _name, "email": _email, "password": _hashed_password}},
        )
        resp = jsonify("User updated successfully!")
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route("/user/<id>", methods=["GET"])
def get_user(id):
    user = mongo.db.user.find_one({"_id": ObjectId(id)})
    if user:
        resp = jsonify(
            {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "password": user["password"],
            }
        )
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route("/users", methods=["GET"])
def get_users():
    try:
        users_cursor = mongo.db.user.find()  # Fetch users as cursor
        print(users, "here")
        users = list(users_cursor)  # Convert cursor to list of dictionaries

        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])

        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error=None):
    message = {
        "status": 404,
        "message": "Not Found: " + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


if __name__ == "__main__":
    app.run(debug=True)
