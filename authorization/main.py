from flask import Flask, request,Response;
import json
import re;

from models import database
from models import User;
from configuration import Configuration

from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt

app = Flask(__name__);
app.config.from_object ( Configuration )
database.init_app ( app )






@app.route("/register_customer",methods=["POST"])
def register_customer():
    forename=request.json.get('forename','');
    surname=request.json.get('surname','');
    email=request.json.get('email','');
    password=request.json.get('password','');
    role='customer';

    if (len(forename)==0):
        return Response(json.dumps({"message":"Field forename is missing."}),status=400);

    if (len(surname)==0):
        return Response(json.dumps({"message":"Field surname is missing."}),status=400);

    if (len(email)==0):
        return Response(json.dumps({"message":"Field email is missing."}),status=400);

    if (len(password)==0):
        return Response(json.dumps({"message":"Field password is missing."}),status=400);

    regexEmail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+');

    if (not regexEmail.fullmatch(email)):
        return Response(json.dumps({"message":"Invalid email."}), status=400);

    if (len(password)<8):
        return Response(json.dumps({"message":"Invalid password."}),status=400);



    u = User.query.filter_by(email=email).first()

    if (u is not None):
        return Response(json.dumps({"message":"Email already exists."}),status=400);

    user=User(email=email,password=password,forename=forename,surname=surname,role=role);

    database.session.add(user);
    database.session.commit();

    return Response(status=200);


@app.route("/register_courier",methods=["POST"])
def register_courier():
    forename = request.json.get('forename', '');
    surname = request.json.get('surname', '');
    email = request.json.get('email', '');
    password = request.json.get('password', '');
    role = 'courier';

    if (len(forename) == 0):
        return Response(json.dumps({"message": "Field forename is missing."}), status=400);

    if (len(surname) == 0):
        return Response(json.dumps({"message": "Field surname is missing."}), status=400);

    if (len(email) == 0):
        return Response(json.dumps({"message": "Field email is missing."}), status=400);

    if (len(password) == 0):
        return Response(json.dumps({"message": "Field password is missing."}), status=400);

    regexEmail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+');

    if (not regexEmail.fullmatch(email)):
        return Response(json.dumps({"message": "Invalid email."}),status=400);

    if (len(password) < 8):
        return Response(json.dumps({"message": "Invalid password."}), status=400);

    u = User.query.filter_by(email=email).first()

    if (u is not None):
        return Response(json.dumps({"message": "Email already exists."}), status=400);

    user = User(email=email, password=password, forename=forename, surname=surname, role=role);

    database.session.add(user);
    database.session.commit();

    return Response(status=200);


jwt=JWTManager(app)

@app.route("/login",methods=["POST"])
def login():
    email = request.json.get('email', '');
    password = request.json.get('password', '');

    if (len(email) == 0):
        return Response(json.dumps({"message": "Field email is missing."}), status=400);

    if (len(password) == 0):
        return Response(json.dumps({"message": "Field password is missing."}), status=400);

    regexEmail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+');

    if (not regexEmail.fullmatch(email)):
        return Response(json.dumps({"message": "Invalid email."}),status=400);

    u = User.query.filter_by(email=email,password=password).first()

    if (u is None):
        return Response(json.dumps({"message": "Invalid credentials."}), status=400);

    a={
        "forename":u.forename,
        "surname":u.surname,
        "email":u.email,
        "password":u.password,
        "role":u.role
    }

    accessToken=create_access_token(identity=u.email,additional_claims=a);

    return Response(json.dumps({'accessToken':accessToken}),status=200);



@app.route("/delete", methods=["POST"])
@jwt_required()
def delete():


    a = get_jwt()
    if (not "owner" in a["role"] and not "customer" in a["role"] and not "courier" in a["role"]):
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401);

    identity=get_jwt_identity()

    user=User.query.filter_by(email=identity).first();
    if (user is None):
        return Response(json.dumps({'message': 'Unknown user.'}), 400)


    database.session.delete(user);
    database.session.commit();

    return Response(status=200)



if (__name__=="__main__"):
    database.init_app(app)
    app.run(debug=True,host="0.0.0.0",port=5001);


