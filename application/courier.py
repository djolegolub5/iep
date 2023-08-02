from flask import Flask, request, Response;
import json
from web3 import Web3
from web3.exceptions import ContractLogicError
from models import database, Order
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


@app.route("/orders_to_deliver", methods=["GET"])
@role_check("courier")
def orders_to_deliver():
    orders=Order.query.filter_by(status="CREATED").all();
    orders=[o.asJSON() for o in orders]
    return Response(json.dumps({"orders":orders}),200);

def read_file ( path ):
    with open ( path, "r" ) as file:
        return file.read ( )


@app.route("/pick_up_order",methods=["POST"])
@role_check("courier")
def pick_up_routes():
    id = request.json.get('id', None);
    address=request.json.get('address',None);

    x = True
    if (id is None):
        return Response(json.dumps({"message": "Missing order id."}), status=400);
    try:
        id = int(id)
        if (id <= 0): x = False
    except:
        x = False
    order = Order.query.filter_by(id=id).first();
    if (not order or not x):
        return Response(json.dumps({"message": "Invalid order id."}), status=400);
    if (order.status != "CREATED"):
        return Response(json.dumps({"message": "Invalid order id."}), status=400);

    if (address is None or len(address)==0):
        return Response(json.dumps({"message": "Missing address."}), status=400)
    try:
        w3 = Web3(Web3.HTTPProvider('http://blockchain:8545'))
        valid=w3.to_checksum_address(address);

    except Exception as e:
        return Response(json.dumps({"message": "Invalid address."}), status=400)

    bytecode = read_file("bytecode.bin")
    abi = read_file("abi.json")

    owner = w3.eth.accounts[0]

    contract = w3.eth.contract(address=order.contract, abi=abi)

    paid=contract.functions.getPaymentStatus().call();
    if (not paid):
        return Response(json.dumps({'message': "Transfer not complete."}), status=400)

    try:
        transaction_hash = contract.functions.bindCourier(address).transact({
            "from": owner
        })
    except ContractLogicError as e:
        revert_message = e.args[0]
        specific_message = revert_message.split(': ')[2]
        split_message = specific_message.split("revert ")
        return Response(json.dumps({"message": str(split_message[1])}), status=400)



    order.status = "PENDING"
    database.session.commit();
    return Response(status=200);

if (__name__=="__main__"):
    database.init_app(app)
    app.run(debug=True,host="0.0.0.0",port=5004);


