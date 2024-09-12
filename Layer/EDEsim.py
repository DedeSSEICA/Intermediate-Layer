import psycopg2
import logging
import os
import maskpass
import argparse
import socket
import encryption
import decryption
import crud
import login
from fastapi import FastAPI

app = FastAPI()
app.include_router(crud.router)
app.include_router(encryption.router_enc)
app.include_router(decryption.router_dec)

database=input("Database name: ")
username=input("User name: ")
password=maskpass.askpass(prompt="Password: ", mask="*")
host=input("Host: ")
port=int(input("Port: "))
table=input("Table name: ")


hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

# Lists to store the number of records and respective durations
num_records = []

#Create an object 
logger=logging.getLogger() 

#Set the threshold of logger to DEBUG 
logger.setLevel(logging.INFO) 

# Function to establish a connection to the PostgreSQL database
def create_connection():
    try:
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=host,
            port=port
        )
        conn.set_session(autocommit=True)
        cursor = conn.cursor()
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY")
        cursor.close()
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        exit()

# Function to enable the pgcrypto extension
def enable_pgcrypto_extension(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    cursor.close()

def menu0():
    conn2 = login.create_connection2()
    print("********** Login System **********")
    print("1.Signup")
    print("2.Login")
    print("3.Exit")
    ch = int(input("Enter your choice: "))
    if ch == 1:
        os.system('cls')
        login.signup(conn2)
    elif ch == 2:
        os.system('cls')
        email=login.login(conn2)
        conn2.close()
        conn = create_connection()
        enable_pgcrypto_extension(conn)
        menu(conn, email)
    elif ch == 3:
        exit()
    else:
        print("Invalid option")
        menu0()

def menu(conn, email):
    print("********** Main Menu **********")
    print("1: Encrypt/Decryption Engine")
    print("2: CRUD Operations")
    print("3: Access Log")
    print("4: Exit")
    option = input("Type the option: ")
    if option == "1":
        os.system('cls')
        menu2(conn, email)
    elif option == "2":
        os.system('cls')
        menu3(conn, email)
    elif option == "3":
        file = open("std.log","r+") 
        print(file.read())
        print()
        input("Press Enter to continue...")
        os.system('cls')
        menu(conn, email)
    elif option == "4":
        conn.close()
        os.system('cls')
        menu0()
    else:
        print("Invalid option")
        menu(conn, email)

def menu2(conn, email):
    print("********** Encrypt/Decryption Engine **********")
    print("1: Insert encrypted data")
    print ("2: Encrypt data")
    print("3: Decrypt data")
    print("4: Decrypt row")
    print("5: Back")
    option = input("Type the option: ")
    if option == "1":
        encryption.encrypt_new_data(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu2(conn, email)
    elif option == "2":
        encryption.encrypt_data(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu2(conn, email)
    elif option == "3":
        decryption.decrypt_data(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu2(conn, email)
    elif option == "4":
        decryption.decrypt_row(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu2(conn, email)
    elif option == "5":
        os.system('cls')
        menu(conn, email)

def menu3(conn, email):
    print("********** CRUD Operations **********")
    print("1: Insert data")
    print("2: Update data")
    print("3: Delete table")
    print("4: Delete row")
    print("5: Create table")
    print("6: Show table")
    print("7: Exit")
    option = input("Type the option: ")
    if option == "1":
        crud.insert_data(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu3(conn, email)
    elif option == "2":
        crud.update_data(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu3(conn, email)
    elif option == "3":
        crud.delete_table(conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu3(conn, email)
    elif option == "4":
        crud.delete_row(table, conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu3(conn, email)
    elif option == "5":
        crud.create_table(conn, email)
        input("Press Enter to continue...")
        os.system('cls')
        menu3(conn, email) 
    elif option == "6":
        crud.get_table(table, conn)
        input("Press Enter to continue...")
        logging.info(f"{IPAddr} {email} - Table showed")
        os.system('cls')
        menu3(conn, email)
    elif option == "7":
        os.system('cls')
        menu(conn, email)
    else:
        print("Invalid option")
        menu3(conn, email)

# Main function
def main():
    #delete_table("simulation", conn)
    #create_table(conn)
    input("Press Enter to continue...")
    os.system('cls')
    menu0()

# Execute the main function
if __name__ == '__main__':
    main()