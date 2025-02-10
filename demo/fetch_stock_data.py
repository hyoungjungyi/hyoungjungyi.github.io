import pymysql
import os

# 🔹 Load MySQL credentials from environment variables
DB_HOST = "stock-database-1.cluster-c1u28umigs1q.eu-west-2.rds.amazonaws.com"
DB_USER = "admin"
DB_PASSWORD = os.getenv("MYSQL_PWD")  # Retrieve password from environment variable
DB_NAME = "stock"

# 🔹 Establish connection to MySQL RDS
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    cursorclass=pymysql.cursors.DictCursor  # Fetch results as dictionaries
)

try:
    with connection.cursor() as cursor:
        # 🔹 Define SQL query
        sql_query = """
        SELECT `price`.`idprice`,
               `price`.`date`,
               `price`.`ticker`,
               `price`.`start_price`,
               `price`.`end_price`
        FROM `stock`.`price`;
        """
        cursor.execute(sql_query)
        
        # 🔹 Fetch all results
        results = cursor.fetchall()
        
        # 🔹 Print retrieved data
        for row in results:
            print(row)  

finally:
    connection.close()  # 🔹 Close the database connection

