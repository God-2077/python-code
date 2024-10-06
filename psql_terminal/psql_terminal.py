#!/usr/bin/python
# -*- coding: UTF-8 -*-

import psycopg2
import sys

connection = None  # 初始化为 None
connection_string = "postgresql://aaaaaaa:[YOUR-PASSWORD]@aaaaaaaaaa.aa.aa:6543/aaaaa" # 你的url

try:
    connection = psycopg2.connect(connection_string)
    cursor = connection.cursor()
    
    print("Connected to the database. Enter SQL commands to execute, or type 'exit' to quit.")
    
    while True:
        query = input("postgres=# ")
        
        if query.lower() in ('exit', 'quit', '\q'):
            break
        
        try:
            cursor.execute(query)
            if cursor.description:
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            else:
                connection.commit()
                print(f"Executed: {cursor.rowcount} rows affected.")
        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()

except Exception as error:
    print("Error while connecting to PostgreSQL:", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
