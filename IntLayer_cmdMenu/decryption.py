import psycopg2
import logging
import EDEsim
import maskpass
import crud
    
def decrypt_row(table, conn, email):
    crud.get_table(table, conn)
    try:
        cursor = conn.cursor()
          
        id=input("Type the id: ")
        password = maskpass.askpass(prompt="Password:", mask="*")

        cursor.execute(f"SELECT * FROM {table} WHERE id = {id}")
        
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        column_names = ', '.join(column_names)
        cursor.execute(f"SELECT {column_names} FROM {table} WHERE id = {id}")
        value=cursor.fetchall()
        row=value[0]
        query=f"UPDATE {table} SET ({column_names})="
        column_names = column_names.split(', ')
        for i in range(len(column_names)): 
            if i == 0:
                query = query + f"(PGP_SYM_DECRYPT(%s::bytea, '{password}')"
            else:
                query = query + f", PGP_SYM_DECRYPT(%s::bytea, '{password}')"
        query = query + f") WHERE id = {id}"
        cursor.execute(query, row)
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Data decrypted")
        crud.get_table(table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to encrypt data failed")
        decrypt_row(table, conn, email)

def decrypt_data(table, conn, email):
    crud.get_table(table, conn)
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        id=input("Type the id: ")
        attr = input("Type the column: ")
        password = maskpass.askpass(prompt="Password:", mask="*")
        cursor.execute(f"SELECT {attr} FROM {table} WHERE id = '{id}'")
        data = cursor.fetchone()
        query = f"UPDATE {table} SET {attr} = PGP_SYM_DECRYPT(%s::bytea, %s) WHERE id = {id}"
        cursor.execute(query, (data, password))
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Data decrypted")
        crud.get_table(table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to decrypt data failed")
        decrypt_data(table, conn, email)