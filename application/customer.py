from datetime import datetime
from flask import Flask, request, Response;
import json
from web3 import Web3, Account
from web3.exceptions import ContractLogicError

from models import database, Product, Category, CategoriesOfProducts, Order, OrdersOfProducts
from configuration import Configuration

from sqlalchemy import and_

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


@app.route("/search", methods=["GET"])
@role_check("customer")
def update():
    name=request.args.get('name')
    category=request.args.get('category')

    if (name is None) :name=''
    if (category is None) : category=''
    categories = Category.query.join(CategoriesOfProducts).join(Product).filter(
            and_(
                *[
                    Category.name.like(f"%{category}%"),
                    Product.name.like(f"%{name}%")
                ]
            )
        ).group_by(Category.id).with_entities(Category.name).all()

    products =  Product.query.join(CategoriesOfProducts).join(Category).filter(
            and_(
                *[
                    Category.name.like(f"%{category}%"),
                    Product.name.like(f"%{name}%")
                ]
            )
        ).group_by(Product.id).all()

    p=[]
    c=[]
    for cat in categories:
        c.append(cat[0])
    for prod in products:
        pcd=[]
        for product_cat in prod.categories:
            pcd.append(product_cat.name)


        p.append({
            "categories": pcd,
            "id": prod.id,
            "name": prod.name,
            "price": prod.price,
        })



    return Response(json.dumps({"categories":c,"products": p}),status=200)


def read_file ( path ):
    with open ( path, "r" ) as file:
        return file.read ( )



@app.route("/order", methods=["POST"])
@role_check("customer")
def order():
    requests=request.json.get('requests','');
    address=request.json.get('address','');

    if (len(requests)==0) :
        return Response(json.dumps({"message": "Field requests is missing."}), status=400)

    identity = get_jwt_identity()


    i=0;

    req=[];
    price=0;
    for r in requests:
        try:
            r['id']
        except:
            return Response(json.dumps({"message": "Product id is missing for request number {}.".format(i)}), status=400);
        try:
            r['quantity']
        except:
            return Response(json.dumps({"message": "Product quantity is missing for request number {}.".format(i)}), status=400);
        try:
            if (int(r['id'])<=0):
                return Response(json.dumps({"message": "Invalid product id for request number {}.".format(i)}), status=400);
        except:
            return Response(json.dumps({"message": "Invalid product id for request number {}.".format(i)}), status=400);
        try:
            if (r['quantity']<=0):
                return Response(json.dumps({"message": "Invalid product quantity for request number {}.".format(i)}), status=400);
        except:
            return Response(json.dumps({"message": "Invalid product quantity for request number {}.".format(i)}),
                            status=400);

        product=Product.query.filter_by(id=r['id']).first();

        if (product is None):

            return Response(json.dumps({"message": "Invalid product for request number {}.".format(i)}), status=400);

        i+=1;
        price+=product.price*r['quantity'];

        req.append(r);

    if (len(address)==0) :
        return Response(json.dumps({"message": "Field address is missing."}), status=400)

    try:
        w3 = Web3(Web3.HTTPProvider('http://blockchain:8545'))
        valid=w3.to_checksum_address(address);

    except Exception as e:
        return Response(json.dumps({"message": "Invalid address."}), status=400)







    bytecode = read_file("bytecode.bin")
    abi = read_file("abi.json")

    owner = w3.eth.accounts[0]

    contract=w3.eth.contract(abi=abi,bytecode=bytecode);

    transaction_hash = contract.constructor(valid, int(price)).transact({
        "from": owner
    });

    receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    contract = w3.eth.contract(address=receipt.contractAddress, abi=abi)
    state_variable = contract.functions.getCustomer().call()



    order=Order(price=price,status="CREATED",date=datetime.today(),email=identity,contract=receipt.contractAddress);
    database.session.add(order);
    database.session.flush();
    database.session.commit();

    for r in req:
        op=OrdersOfProducts(productId=r['id'],orderId=order.id,quantity=r['quantity']);
        database.session.add(op);
        database.session.flush();
        database.session.commit();


    return Response(json.dumps({"id":order.id}),status=200)


@app.route("/status", methods=["GET"])
@role_check("customer")
def status():
    identity = get_jwt_identity()

    orders=Order.query.filter_by(email=identity).all();
    ordersResult=[]
    for order in orders:
        pos=OrdersOfProducts.query.filter_by(orderId=order.id).all();
        products=[]
        for p in pos:
            product=Product.query.filter_by(id=p.productId).first();
            categories = Category.query.join(CategoriesOfProducts).filter(
                CategoriesOfProducts.productId == product.id
            ).group_by(Category.id).with_entities(Category.name).all()
            categories=[item for t in categories for item in t]
            product=product.asJSONPO(categories,p.quantity)
            products.append(product);
        o=order.asJSONProducts(products);
        ordersResult.append(o);
    return Response(json.dumps({"orders":ordersResult}),status=200);

@app.route("/delivered", methods=["POST"])
@role_check("customer")
def delivered():
    id=request.json.get('id',None);
    keys=request.json.get('keys',None);
    passphrase=request.json.get('passphrase',None);

    x=True
    if (id is None):
        return Response(json.dumps({"message": "Missing order id."}), status=400);
    try:
        id=int(id)
        if (id<=0): x=False
    except:
        x=False
    order=Order.query.filter_by(id=id).first();
    if (not order or not x):
        return Response(json.dumps({"message": "Invalid order id."}), status=400);
    if (order.status!="PENDING"):
        return Response(json.dumps({"message": "Invalid order id."}), status=400);

    if (keys is None or len(keys)==0):
        return Response(json.dumps({"message": "Missing keys."}), status=400);

    if (passphrase is None or len(passphrase)==0):
        return Response(json.dumps({"message": "Missing passphrase."}), status=400);
    w3 = Web3(Web3.HTTPProvider('http://blockchain:8545'))
    bytecode = read_file("bytecode.bin")
    abi = read_file("abi.json")
    contract = w3.eth.contract(address=order.contract, abi=abi)
    keys=keys.replace("'", '"');


    keys = json.loads(keys)

    try:
        address = w3.to_checksum_address ( keys["address"] )
        privateKey = Account.decrypt(keys, passphrase).hex()
    except ValueError as e:
        return Response(json.dumps({'message':"Invalid credentials."}),status=400)



    customer=contract.functions.getCustomer().call();
    if (customer!=address):
        return Response(json.dumps({'message':"Invalid customer account."}),status=400)

    paid=contract.functions.getPaymentStatus().call();
    if (not paid):
        return Response(json.dumps({'message': "Transfer not complete."}), status=400)

    picked=contract.functions.getPickupStatus().call();
    if (not picked):
        return Response(json.dumps({'message': "Delivery not complete."}), status=400)

    try:
        transaction = contract.functions.confirmDelivery().transact({
            'from': address
        })

    except ContractLogicError as e:
        revert_message = e.args[0]
        specific_message = revert_message.split(': ')[2]
        split_message = specific_message.split("revert ")
        return Response(json.dumps({"message": str(split_message[1])}), status=400)



    order.status="COMPLETE"
    database.session.commit();
    return Response(status=200);


@app.route("/pay", methods=["POST"])
@role_check("customer")
def pay():
    id=request.json.get('id',None);
    keys=request.json.get('keys',None);
    passphrase=request.json.get('passphrase',None);

    x=True
    if (id is None):
        return Response(json.dumps({"message": "Missing order id."}), status=400);
    try:
        id=int(id)
        if (id<=0): x=False
    except:
        x=False
    order=Order.query.filter_by(id=id).first();
    if (not order or not x):
        return Response(json.dumps({"message": "Invalid order id."}), status=400);

    if (keys is None or len(keys)==0):
        return Response(json.dumps({"message": "Missing keys."}), status=400);

    if (passphrase is None or len(passphrase)==0):
        return Response(json.dumps({"message": "Missing passphrase."}), status=400);


    w3 = Web3(Web3.HTTPProvider('http://blockchain:8545'))
    bytecode = read_file("bytecode.bin")
    abi = read_file("abi.json")
    contract = w3.eth.contract(address=order.contract, abi=abi)
    keys=json.loads(keys)




    try:
        address = w3.to_checksum_address ( keys["address"] )
        privateKey = Account.decrypt(keys, passphrase).hex()
    except ValueError as e:
        return Response(json.dumps({'message':"Invalid credentials."}),status=400)

    if (w3.eth.get_balance(address)<order.price):
        return Response(json.dumps({'message':"Insufficient funds."}),status=400)


    paid=contract.functions.getPaymentStatus().call();
    if (paid):
        return Response(json.dumps({'message': "Transfer already complete."}), status=400)



    transaction = {
            'from': address,
            'value': int(order.price)
    }

    transaction=contract.functions.transferFunds().transact(transaction)


    return Response(status=200)





if (__name__=="__main__"):
    database.init_app(app)
    app.run(debug=True,host="0.0.0.0",port=5003);


