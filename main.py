import psycopg2

with psycopg2.connect(database="netology_db", user="postgres", password="postgres") as conn:
    with conn.cursor() as cur:

        def create_table():
            cur.execute("""
            CREATE TABLE IF NOT EXISTS clients(
                client_id SERIAL PRIMARY KEY,
                first_name VARCHAR(60) NOT NULL,
                last_name VARCHAR(60) NOT NULL,
                email VARCHAR(255)
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS phones(
                phone_id SERIAL PRIMARY KEY,
                client_id INT,
                phone_number VARCHAR(20),
                FOREIGN KEY (client_id) REFERENCES clients(client_id)
            );
            """)
            conn.commit()

        def insert_client(first_name: str, last_name: str, email: str, phone_number: str =None):
            cur.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING client_id;
            """, (first_name, last_name, email))
            conn.commit()
            show_client_id = cur.fetchone()[0]
            return show_client_id

        def insert_phone_number(client_id: int, phone_number: str):
            cur.execute("""
            INSERT INTO phones (client_id, phone_number)
            VALUES (%s, %s);
            """, (client_id, phone_number))
            conn.commit()
            cur.execute("""
            SELECT * FROM phones;
            """)
            res = cur.fetchone()[2]
            print('Phone_Number:', res)
            return res

        def show_clients_info():
            cur.execute("""
            SELECT * FROM clients;
            """)
            res = cur.fetchall()
            print('Client:', res)
            return res

        def change_client_info(first_name: str, last_name: str, client_id: int, email=None):
            cur.execute("""
            UPDATE clients SET first_name=%s, last_name=%s, email=%s
            WHERE client_id=%s;
            """, (first_name, last_name, email, client_id))
            conn.commit()
            cur.execute("""
            SELECT * FROM clients;
            """)
            res = cur.fetchall()
            print('Client Info After Changing: ', res)
            return res

        def delete_phone(client_id: int):
            cur.execute("""
            DELETE FROM phones
            WHERE client_id = %s;
            """, (client_id,))
            conn.commit()
            return "Phone deleted"

        def delete_client(client_id: int):
            cur.execute("""
            DELETE FROM clients
            WHERE client_id = %s;
            """, (client_id,))
            conn.commit()
            return f"Client {client_id} deleted"

        def reset_autoincrement():
            cur.execute("""
            ALTER SEQUENCE public.clients_client_id_seq RESTART WITH 1;
            """)
            cur.execute("""
            ALTER SEQUENCE public.phones_phone_id_seq RESTART WITH 1;;
            """)
            conn.commit()
            return f"Autoincrement for clients and phones tables reseted"

        def find_client(first_name=None, last_name=None, email=None, phone=None):
            query = """
            SELECT clients.*
            FROM clients
            LEFT JOIN phones ON clients.client_id = phones.client_id
            WHERE 1=1
            """
            params = []

            if first_name is not None:
                query += " AND clients.first_name = %s"
                params.append(first_name)
            if last_name is not None:
                query += " AND clients.last_name = %s"
                params.append(last_name)
            if email is not None:
                query += " AND clients.email = %s"
                params.append(email)
            if phone is not None:
                query += " AND phones.phone_number = %s"
                params.append(phone)

            cur.execute(query, tuple(params))
            res = cur.fetchall()

            if res:
                print('Client(s) found:', res)
            else:
                print('No clients found.')

            return res

        create_table()
        client_id =insert_client('Андрей', 'Матросов', 'andrmatrosov@mail.ru')
        insert_phone_number(client_id, "+7-999-123-45-67")
        show_clients_info()
        change_client_info("Алексей", 'Воробьев', 1, email="alekvorobyev@mail.ru", )
        (find_client(None, None, None, "+7-999-123-45-67"))
        phone_delete = delete_phone(client_id)
        delete_client(client_id)
        reset_autoincrement()

conn.close()