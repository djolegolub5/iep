import os
import subprocess

from flask import Flask, request,Response;
import json

import requests

from models import database, Product, Category, CategoriesOfProducts
from configuration import Configuration

from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt

app = Flask(__name__);
app.config.from_object ( Configuration )
database.init_app ( app )
jwt=JWTManager(app)

from flask_jwt_extended import jwt_required
from functools import wraps
def role_check ( role ):
    def decorator ( function ):
        @jwt_required ( )
        @wraps ( function )
        def wrapper ( *args, **kwargs ):
            a = get_jwt()

            if (role == a['role']):
                return function(*args, **kwargs)
            else:
                return Response(json.dumps({"msg": "Missing Authorization Header"}), 401)
        return wrapper
    return decorator

def isfloat(num):
    try:
        float(num)
        if (float(num)>0): return True;
        else: return False;
    except ValueError:
        return False


@app.route("/update", methods=["POST"])
@role_check("owner")
def update():
    file=request.files.get("file",None)
    if not file:
        return Response(json.dumps({
            "message": "Field file is missing."
        }), 400);

    content = file.stream.read().decode("utf-8-sig")



    i=0;
    niz=[]

    for line in content.split("\n"):
        product=line.split(",");

        if (len(product)!=3):
            return Response(json.dumps({"message":"Incorrect number of values on line "+str(i)+"."}),400);

        price=product[2];
        if (not isfloat(price)):
            return Response(json.dumps({"message":"Incorrect price on line "+str(i)+"."}),400);
        line.rstrip("\r")
        name=product[1]
        product[2]=product[2].rstrip("\r");
        u = Product.query.filter_by(name=name).first()

        if (u is not None):
            return Response(json.dumps({"message":"Product {} already exists.".format(name)}),400);


        i+=1;

        niz.append(product);
    print(niz);
    for line in niz:
        p = line
        price=p[2];
        name=p[1];

        product=Product(name=name,price=price)
        database.session.add(product);
        database.session.flush();

        database.session.commit();

        productId=product.id;

        categories=p[0].split("|");
        for category in categories:
            c = Category.query.filter_by(name=category).first()



            if (c is None):
                c=Category(name=category);
                database.session.add(c);
                database.session.flush();

                database.session.commit();

            categoryId=c.id;

            pc=CategoriesOfProducts(productId=productId,categoryId=categoryId);
            database.session.add(pc);
            database.session.flush();

            database.session.commit();



    return Response(status=200)

@app.route("/product_statistics", methods=["GET"])
@role_check("owner")
def product_statistics():
    res=requests.get(f"http://spark:5000/product")
    return Response(json.dumps(res.json()),200);

@app.route("/category_statistics", methods=["GET"])
@role_check("owner")
def category_statistics():
    res=requests.get(f"http://spark:5000/category")
    return Response(json.dumps(res.json()),200);


if (__name__=="__main__"):
    database.init_app(app)
    app.run(debug=True,host="0.0.0.0",port=5002);


