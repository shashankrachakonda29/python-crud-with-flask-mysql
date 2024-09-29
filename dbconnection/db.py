import mysql.connector
import logging
database_name = "" 
def connection_Database():
    try:
        connection=mysql.connector.connect(host="localhost",user="root",passwd="2908",database=database_name)
        return connection.cursor(),connection
    except mysql.connector.Error as e:
        logging.error("Error connecting to database: %s", e)
        return None, None
cur_obj, connection = connection_Database()
if cur_obj is not None and connection is not None:  # Ensure both are not None:
    with connection:
        database_name = 'pythontestdb'  # Here we specify the database we want to use or create.
        # Check if the database exists
        sql = f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = '{database_name}'"
        cur_obj.execute(sql)
        myresult = cur_obj.fetchone()
        
        if myresult[0] == 1:
            print("Database exists.")
        else:
            print("Database does not exist.")
            sql = f"CREATE DATABASE {database_name}"
            try:
                cur_obj.execute(sql)
                print(f"Database '{database_name}' created successfully.")
            except mysql.connector.Error as err:
                if err.errno == 1007:  # Error code for database already exists
                    print(f"Database '{database_name}' already exists.")
                else:
                    print(f"Error creating database: {err}")
        
else:
    print("Failed to connect to the database.")
