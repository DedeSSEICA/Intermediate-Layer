import psycopg2
import logging
import EDEsim
import maskpass
import crud

# FUNCTION TO ENCRYPT NEW DATA
def encrypt_new_data(table, conn, email):
    # Generate a new key pair
    #(public_key, private_key) = rsa.newkeys(2048)
    crud.get_table(table, conn)
    try:
        #password=getpass.getpass("New password: ")
        password = maskpass.askpass(prompt="New password:", mask="*")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        value=[]
        column_names = ', '.join(column_names)
        
        query=f"INSERT INTO {table} ({column_names}) "
        column_names = column_names.split(', ')
        for i in range(len(column_names)): 
            value.append(input(f"Type the value for {column_names[i]}: "))
            if i == 0:
                query = query + f"VALUES (PGP_SYM_ENCRYPT('{value[i]}', '{password}')"
            else:
                query = query + f", PGP_SYM_ENCRYPT('{value[i]}', '{password}')"
        
        query = query + " )"
        cursor.execute(query)
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Data encrypted")
        crud.get_table(table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to encrypt data failed")
        encrypt_new_data(table, conn, email)

def encrypt_data(table, conn, email):
    crud.get_table(table, conn)
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
                crud.get_table(table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to encrypt data failed")
        encrypt_data(table, conn, email)