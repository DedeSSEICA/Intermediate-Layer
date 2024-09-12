import psycopg2
import logging
import tabulate
import EDEsim

# FUNTION TO DELETE TABLE
def delete_table(conn, email):
    try:
        d_table=input("Name of the table you want to delete: ")
        cursor = conn.cursor()
        query = "DROP TABLE " + d_table
        cursor.execute(query)
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Table {d_table} deleted")
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to delete table failed")
        delete_table(conn, email)

# FUNCTION TO CREATE TABLE
def create_table(conn, email):
    n_table=input("Type the table name: ")
    attr = int(input("Type the number of columns: "))
    try:
        cursor = conn.cursor()
        for i in range(attr):
            column = input(f"Type the column {i+1} name: ")
            data_type = "VARCHAR(1000)"
            if i == 0:
                query = "CREATE TABLE IF NOT EXISTS " + n_table + " ( " + column + " " + data_type
            else:
                query = query + ", " + column + " " + data_type
        
        query = query + " )"
        cursor.execute(query)
        cursor.execute(f"ALTER TABLE {n_table} ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY")
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Table created")
        get_table(n_table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to create table failed")
        create_table(conn, email)

# FUNCTION TO SHOW TABLE
def get_table(table, conn):
    column_names = []
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} ORDER BY id ASC"
    cursor.execute(query)
    column_names = [desc[0] for desc in cursor.description]
    header = column_names
    rows=[]
    row=cursor.fetchone()
    while row is not None:
        truncated_row = [str(item)[:20] for item in row]
        rows.append(truncated_row)
        row=cursor.fetchone()
    print(tabulate.tabulate(rows, headers=header, tablefmt='pretty'))
    cursor.close()

# FUNCTION TO INSERT DATA MANUALLY
def insert_data(table, conn, email):
    try:
        get_table(table, conn)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        value=[]
        for i in range(len(column_names)):
            value.append(input(f"Type the value for {column_names[i]}: "))
        column_names = ', '.join(column_names)
        value = "', '".join(value)
        query = f"INSERT INTO {table} ({column_names}) VALUES ('{value}')"
        cursor.execute(query)
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Table inserted")
        get_table(table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to insert data failed")
        insert_data(table, conn, email)

# FUNCTION TO UPDATE DATA
def update_data(table, conn, email):
    try:
        get_table(table, conn)
        attr = input("Type the column: ")
        id = input("Type the id: ")
        new_data = input("Type the new data: ")
        cursor = conn.cursor()
        query = f"UPDATE {table} SET {attr} = '{new_data}' WHERE id = '{id}'"
        cursor.execute(query)
        cursor.close()
        logging.info(f"{EDEsim.IPAddr} {email} - Table updated")
        get_table(table, conn)
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        logging.info(f"{EDEsim.IPAddr} {email} - Attempt to update data failed")
        update_data(table, conn, email)