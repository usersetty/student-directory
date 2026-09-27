from database import get_connection

try:
    connection=get_connection()
    print("Database connected successfully")
    connection.close()
except Exception as e:
    print("Database failed")
    print(e)