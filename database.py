# database.py
# This file manages the MySQL database connection.
# We use mysql-connector-python to connect to our MySQL database.

import mysql.connector
from mysql.connector import Error

# Database configuration — change these values to match your MySQL setup
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',   # Change this to your MySQL root password
    'database': 'personal_finance',
    'port': 3306
}

def get_db_connection():
    """
    Creates and returns a new connection to the MySQL database.
    Returns None if the connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """
    Reads schema.sql and runs all the CREATE TABLE statements.
    Call this once when setting up the project for the first time.
    """
    connection = get_db_connection()
    if connection is None:
        print("Could not connect to database. Please check your MySQL settings in database.py")
        return
    
    cursor = connection.cursor()
    
    # Read the SQL schema file
    with open('database/schema.sql', 'r') as schema_file:
        sql_content = schema_file.read()
    
    # Split by semicolons to get individual statements
    sql_statements = sql_content.split(';')
    
    for statement in sql_statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):  # Skip empty lines and comments
            try:
                cursor.execute(statement)
            except Error as e:
                # Ignore errors for statements that already ran (e.g. CREATE TABLE IF NOT EXISTS)
                if 'already exists' not in str(e).lower():
                    print(f"SQL Error: {e}")
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Database initialized successfully!")
