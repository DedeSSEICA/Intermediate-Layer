import os
import psycopg2
import hashlib
import logging
import maskpass
import EDEsim
from fastapi import FastAPI

app = FastAPI()

# Function to establish a connection to the PostgreSQL database
def create_connection2():
    try:
        conn2 = psycopg2.connect(
            database="login",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5433"
        )
        conn2.set_session(autocommit=True)
        cursor2 = conn2.cursor()
        cursor2.close()
        return conn2
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        exit()

def signup(conn2):
    email = input("Enter username: ")
    cursor2 = conn2.cursor()
    cursor2.execute(f"SELECT username FROM users WHERE username = '{email}'")
    stored_email = cursor2.fetchone()
    if stored_email is not None:
        print("Username already exists! \n")
        signup(conn2)
    else:
        pwd = maskpass.askpass(prompt="Enter password: ", mask="*")
        #pwd = input("Enter password: ")
        #conf_pwd = input("Confirm password: ")
        conf_pwd = maskpass.askpass(prompt="Confirm password: ", mask="*")    
        if conf_pwd == pwd:
            enc = conf_pwd.encode()
            hash1 = hashlib.md5(enc).hexdigest()
            cursor2 = conn2.cursor()
            cursor2.execute(f"INSERT INTO users (username, password) VALUES ('{email}', '{hash1}')")
            print("You have registered successfully!")
            input("Press Enter to continue...")
            os.system('cls')
            EDEsim.menu0(conn2)
        else:
            print("Password is not same as above! \n")
            signup(conn2)

def login(conn2):
    email = input("Enter username: ")
    #pwd = input("Enter password: ")
    pwd = maskpass.askpass(prompt="Enter password: ", mask="*")
    auth = pwd.encode()
    auth_hash = hashlib.md5(auth).hexdigest()
    cursor2 = conn2.cursor()
    cursor2.execute(f"SELECT password FROM users WHERE username = '{email}'")
    stored_pwd = cursor2.fetchone()[0]
    if stored_pwd == auth_hash:
        print("Logged in Successfully!")
        logging.info(f"{EDEsim.IPAddr} {email} - Connection info: Database: {EDEsim.database} Username: {EDEsim.username} Host: {EDEsim.host} Port: {str(EDEsim.port)}")
        input("Press Enter to continue...")
        os.system('cls')
        return email
    else:
        print("Login failed! \n")
        login(conn2)