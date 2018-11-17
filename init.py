from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.sql.functions import *
from models import *

INPUT_FILE = '7210_1.csv'
sc = SparkContext.getOrCreate()
sqlContext = SQLContext(sc)

df = sqlContext.read.load(INPUT_FILE,
                          format='com.databricks.spark.csv',
                          header='true',
                          inferSchema='true')

columns_to_drop = [c for c in df.columns if c not in ('id', 'brand', 'colors', 'dateAdded')]
# Remove extra columns, Ignore records with any of the columns as null
df = df.drop(*columns_to_drop)
df = df.na.drop(subset=['colors', 'id', 'brand', 'dateAdded'])

df = df.withColumn('date', to_date(df['dateAdded']))

# Recently added product
# ORDER BY dateAdded DESC, GROUP BY date
window = Window.partitionBy(df['date']).orderBy(df['dateAdded'].desc())
recent_product_by_date = df.select('*', row_number().over(window).alias('row_number')).filter(col('row_number') <= 1)
for p in recent_product_by_date.collect():
    RecentProduct(str(p.date)).set(Product(p.id, p.brand, p.colors))

# Brand Count per Day
brand_count = df.groupBy(col('date'), col('brand')).count().sort(col('date').desc(), col('count').desc()).withColumnRenamed('count', 'additions')
for bc in brand_count.collect():
    BrandCount(str(bc.date)).set(bc.brand, bc.additions)

# Colors Recent 10 Products
cdf = df.select('*', explode(split(col('colors'), ',')).alias('color'))
window = Window.partitionBy(cdf['color']).orderBy(cdf['dateAdded'].desc())
recent_products_by_color = cdf.select('*', row_number().over(window).alias('row_number')).filter(col('row_number') <= 10)
for p in recent_products_by_color.collect():
    RecentProductsByColor(p.color).add(Product(p.id, p.brand, p.colors, str(p.dateAdded)), p.dateAdded.timestamp())