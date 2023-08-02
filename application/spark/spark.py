import os
import subprocess

from flask import Flask, request,Response, jsonify;
import json



app = Flask(__name__);




@app.route("/category", methods=["GET"])
def category():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/category_statistics.py"
    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
    result = subprocess.check_output(["/template.sh"])

    with open('cs.json', 'r') as f:
        data = json.load(f)
    return jsonify(data);


@app.route("/product", methods=["GET"])
def product():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/product_statistics.py"
    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
    result = subprocess.check_output(["/template.sh"])

    with open('ps.json', 'r') as f:
        data = json.load(f)

    return jsonify(data);




if (__name__=="__main__"):
    app.run(debug=True,host="0.0.0.0",port=5000);


