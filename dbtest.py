import MySQLdb

try:
    db = MySQLdb.connect(
        host="localhost",
        user="root",          # Replace with your MySQL username
        passwd="ridds1234",      # Replace with your MySQL password
        db="study_planner_db" # Replace with your database name
    )
    print("Database connected successfully!")
    db.close()
except MySQLdb.Error as e:
    print(f"Error connecting to MySQL: {e}")