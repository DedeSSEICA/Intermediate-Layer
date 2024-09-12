import psycopg2
import logging
import EDEsim
import maskpass
import crud
from typing import List
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

router_enc = APIRouter()

class EncryptionData(BaseModel):
    password: str
    values: List[str]


# FUNCTION TO ENCRYPT NEW DATA
# $encryptionData = @{
#    password = "power"
#    values = @("value1", "value2", "value3") 
#}
# $body = ConvertTo-Json -InputObject $columns
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/full_encryption" -Method Post -Body $body -ContentType "application/json"
@router_enc.post("/full_encryption")
def encrypt_new_data(encryption_data: EncryptionData):
    try:
        conn=crud.connect_and_log()
        cursor = conn.cursor()
        table = EDEsim.table
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        value=[]
        column_names = ', '.join(column_names)

        query=f"INSERT INTO {table} ({column_names}) "
        #column_names = column_names.split(', ')
        for i, value in enumerate(encryption_data.values): 
            #value.append(input(f"Type the value for {column_names[i]}: "))
            if i == 0:
                query = query + f"VALUES (PGP_SYM_ENCRYPT('{value}', '{encryption_data.password}')"
            else:
                query = query + f", PGP_SYM_ENCRYPT('{value}', '{encryption_data.password}')"
        
        query = query + " )"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        message = f"Encrypted data inserted into table '{table}'"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return message
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to insert encrypted data into table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))

def encrypt_data(table, conn, email):
    try:
        #password=getpass.getpass("Password: ")
        password = maskpass.askpass(prompt="New password:", mask="*")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        data = input("Type the data you want to encrypt: ")
        attr = input("Type the column: ")
        id=input("Type the id: ")
        cursor.execute(f"SELECT {attr} FROM {table} WHERE {attr} = '{data}' AND id = '{id}'")
        datacheck = cursor.fetchone()
        if  datacheck is None:
            print("Data not found")
            encrypt_data(table, conn, email)
        else:
            datacheck = datacheck[0]
            if datacheck is None:
                print("Data not found")
                encrypt_data(table, conn, email)
            else:
                query = f"UPDATE {table} SET {attr} = PGP_SYM_ENCRYPT('{data}', '{password}') WHERE id = '{id}'"
                cursor.execute(query)
                cursor.close()
                logging.info(f"{EDEsim.IPAddr} {email} - Data encrypted")
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to encrypt data failed")
        encrypt_data(table, conn, email)