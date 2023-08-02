import json

from pyspark.sql import SparkSession

import os

from pyspark.sql.functions import col
from pyspark.sql.functions import when
from pyspark.sql.functions import sum

import logging
builder = SparkSession.builder.appName("Category Statistics")

builder = builder\
    .config(
    "spark.driver.extraClassPath",
    "mysql-connector-j-8.0.33.jar"
)

spark = builder.getOrCreate()


categories = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://root:root@shopDB/shop") \
    .option("dbtable", "shop.categories") \
    .load()

cos = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://root:root@shopDB/shop") \
    .option("dbtable", "shop.categories_of_products") \
    .load()

products = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://root:root@shopDB/shop") \
    .option("dbtable", "shop.products") \
    .load()

orders = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://root:root@shopDB/shop") \
    .option("dbtable", "shop.orders") \
    .load()

pos = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://root:root@shopDB/shop") \
    .option("dbtable", "shop.orders_of_products") \
    .load()

result = (

    categories
    .join(cos, cos.categoryId == categories.id,"left")
    .join(pos, cos.productId==pos.productId,"left")
    .join(orders, pos.orderId==orders.id,"left")
    .groupBy(categories.name)
    .agg(
        sum(when(orders.status == "COMPLETE", pos.quantity).otherwise(0)).alias("sold"),
    )
    .select(col("name"))
    .orderBy(col("sold").desc(), col("name").asc())
).collect()


out=[]

for row in result:
    out.append(row.name)

objekat=json.dumps({"statistics":out});

with open("cs.json", "w") as outfile:
    outfile.write(objekat)



spark.stop()