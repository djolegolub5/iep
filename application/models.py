from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


database = SQLAlchemy()
migrate=Migrate()




class CategoriesOfProducts(database.Model):

    __tablename__="categories_of_products"


    id=database.Column(database.Integer, primary_key=True);
    productId=database.Column(database.Integer,database.ForeignKey("products.id"),nullable=False)
    categoryId=database.Column(database.Integer,database.ForeignKey("categories.id"),nullable=False)

class OrdersOfProducts(database.Model):

    __tablename__="orders_of_products"


    id=database.Column(database.Integer, primary_key=True);
    productId=database.Column(database.Integer,database.ForeignKey("products.id"),nullable=False)
    orderId=database.Column(database.Integer,database.ForeignKey("orders.id"),nullable=False)
    quantity=database.Column(database.Integer, nullable=False)



class Product(database.Model):

    __tablename__="products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)

    categories=database.relationship("Category",secondary=CategoriesOfProducts.__table__,back_populates="products")
    orders=database.relationship("Order",secondary=OrdersOfProducts.__table__,back_populates="products")

    def asJSON(self):
        return {
            "id":self.id,
            "name":self.name,
            "price":self.price
        }

    def asJSONPO(self,categories,quantity):

        return {
            "categories":categories,
            "name":self.name,
            "price":self.price,
            "quantity":quantity
        }

class Category(database.Model):
    __tablename__="categories"


    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)

    products=database.relationship("Product",secondary=CategoriesOfProducts.__table__,back_populates="categories")


class Order(database.Model):
    __tablename__="orders"

    id=database.Column(database.Integer, primary_key=True)
    price=database.Column(database.Float,nullable=False)
    status = database.Column(database.String(256), nullable = False)
    contract = database.Column(database.String(256), nullable = False)

    date = database.Column(database.DateTime, nullable = False)

    email = database.Column(database.String(256), nullable=False)
    products=database.relationship("Product",secondary=OrdersOfProducts.__table__,back_populates="orders")


    def asJSONProducts(self,products):
        return {
            "products":products,
            "price":self.price,
            "status":self.status,
            "timestamp":str(self.date)
        }

    def asJSON(self):


        return{
            "id": self.id,
            "email":self.email
        }
