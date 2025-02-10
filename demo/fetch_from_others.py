import os
import pymysql
from sshtunnel import SSHTunnelForwarder

# 🔹 SSH & MySQL Configuration
SSH_HOST = "35.176.222.6"  # Public IP of the EC2 instance
SSH_USER = "ec2-user"
SSH_KEY_FILE = "../stock.pem"  # Path to the PEM key file

RDS_HOST = "stock-database-1.cluster-c1u28umigs1q.eu-west-2.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = os.getenv("MYSQL_PWD")  # 🔥 Retrieve password from environment variable
RDS_DB = "stock"

# 🔹 Establish an SSH tunnel to connect to the RDS database securely
with SSHTunnelForwarder(
    (SSH_HOST, 22),
    ssh_username=SSH_USER,
    ssh_pkey=SSH_KEY_FILE,
    remote_bind_address=(RDS_HOST, 3306),
    local_bind_address=('127.0.0.1', 3306)
) as tunnel:

    # 🔹 Connect to MySQL RDS through the SSH tunnel
    connection = pymysql.connect(
        host="127.0.0.1",  # The SSH tunnel forwards MySQL traffic to this address
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB,
        port=3306,
        cursorclass=pymysql.cursors.DictCursor  # Fetch results as dictionaries
    )

    try:
        with connection.cursor() as cursor:
            # 🔹 Execute SQL query
            sql_query = "SELECT * FROM price LIMIT 5;"
            cursor.execute(sql_query)
            results = cursor.fetchall()

            # 🔹 Print query results
            for row in results:
                print(row)

    finally:
        connection.close()  # 🔹 Close the MySQL connection
