import psycopg2
import maskpass
import socket
import encryption
import decryption
import crud
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
