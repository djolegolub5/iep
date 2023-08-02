import json
from pyspark.sql import SparkSession

import os

from pyspark.sql.functions import col
from pyspark.sql.functions import when
from pyspark.sql.functions import sum


builder = SparkSession.builder.appName("Product Statistics")


builder = builder\
    .config(
    "spark.driver.extraClassPath",
    "mysql-connector-j-8.0.33.jar"
)

spark = builder.getOrCreate()


spark.sparkContext.setLogLevel("WARN")

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
    pos
    .join(products, pos.productId == products.id)
    .join(orders, pos.orderId == orders.id)
    .groupBy(products.name)
    .agg(
        sum(when(orders.status == "COMPLETE", pos.quantity).otherwise(0)).alias("sold"),
        sum(when(orders.status != "COMPLETE", pos.quantity).otherwise(0)).alias("waiting")
    )
    .select(col("name"), col("sold"), col("waiting"))
).collect()

out=[]

for row in result:
    out.append({
        "name":row.name,
        "sold":row.sold,
        "waiting":row.waiting
    });

objekat=json.dumps({"statistics":out});

with open("ps.json", "w") as outfile:
    outfile.write(objekat)



spark.stop()