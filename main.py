import psycopg2

# УДАЛЕНИЕ ТАБЛИЦ
def drop_table():
    cur.execute("""
    DROP TABLE phones;
    DROP TABLE clients;
    """)

# СОЗДАНИЕ ТАБЛИЦ
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

# ДОБАВЛЕНИЕ ИНФОРМАЦИИ В ТАБЛИЦУ КЛИЕНТОВ И ПОЛУЧЕНИЕ ID КЛИЕНТА
def insert_client(first_name: str, last_name: str, email: str):
    cur.execute("""
    INSERT INTO clients (first_name, last_name, email)
    VALUES (%s, %s, %s)
    RETURNING client_id;
    """, (first_name, last_name, email))
    show_client_id = cur.fetchone()[0]
    return show_client_id

# ДОБАВЛЕНИЕ ИНФОРМАЦИИ В ТАБЛИЦУ ТЕЛЕФОННЫХ НОМЕРОВ
def insert_phone_number(client_id: int, phone_number: str):
    cur.execute("""
    INSERT INTO phones (client_id, phone_number)
    VALUES (%s, %s);
    """, (client_id, phone_number))
    cur.execute("""
    SELECT * FROM phones;
    """)
    res = cur.fetchone()[2]
    print('Phone_Number:', res)
    return res

# ВЫВОД ИНФОРМАЦИИ О КЛИЕНТАХ
def show_clients_info():
    cur.execute("""
    SELECT * FROM clients;
    """)
    res = cur.fetchall()
    print('Client:', res)
    return res

# ИЗМЕНЕНИЕ ИНФОРМАЦИИ О КЛИЕНТАХ
def change_client_info(client_id: int, first_name=None, last_name=None, email=None):
    updates = []
    params = []

    if first_name is not None:
        updates.append("first_name = %s")
        params.append(first_name)
    if last_name is not None:
        updates.append("last_name = %s")
        params.append(last_name)
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    if not updates:
        print("Нет полей для изменения.")
        return

    query = f"""
    UPDATE clients
    SET {', '.join(updates)}
    WHERE client_id = %s;
    """

    params.append(client_id)
    cur.execute(query, tuple(params))
    print(f"Client {client_id} info updated.")

# ПОИСК КЛИЕНТА
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

# УДАЛЕНИЕ ИНФОРМАЦИИ О НОМЕРЕ ТЕЛЕФОНА КЛИЕНТА
def delete_phone(client_id: int):
    cur.execute("""
    DELETE FROM phones
    WHERE client_id = %s;
    """, (client_id,))
    return "Phone deleted"

# УДАЛЕНИЕ КЛИЕНТА
def delete_client(client_id: int):
    cur.execute("""
    SELECT phone_number
    FROM clients
    LEFT JOIN phones ON clients.client_id = phones.client_id
    WHERE clients.client_id = %s;
    """, (client_id,))
    phone_output = cur.fetchone()

    if phone_output is not None and phone_output[0] is not None:
        cur.execute("""
        DELETE FROM phones
        WHERE client_id = %s;
        """, (client_id,))
        print (f"Phone {phone_output[0]} deleted")
    else:
        print("Phone not found")

    cur.execute("""
    DELETE FROM clients
    WHERE client_id = %s;
    """, (client_id,))
    print(f"Client {client_id} deleted")
    return

# СБРОС АВТОИНКРЕМЕНТА
def reset_autoincrement():
    cur.execute("""
    ALTER SEQUENCE public.clients_client_id_seq RESTART WITH 1;
    """)
    cur.execute("""
    ALTER SEQUENCE public.phones_phone_id_seq RESTART WITH 1;;
    """)
    return f"Autoincrement for clients and phones tables was reset"

# МЕНЕДЖЕР ПОДКЛЮЧЕНИЯ
with psycopg2.connect(database="netology_db", user="postgres", password="postgres") as conn:
    with conn.cursor() as cur:
        # ВЫЗОВ ФУНКЦИЙ
        drop_table()
        create_table()
        client_id = insert_client('Андрей', 'Матросов', 'andrmatrosov@mail.ru')
        insert_phone_number(client_id, "+7-999-123-45-67")
        show_clients_info()
        change_client_info(client_id=1, last_name='Воробьев')
        show_clients_info()
        (find_client(first_name='Андрей'))
        phone_delete = delete_phone(client_id)
        delete_client(client_id)
        reset_autoincrement()

conn.close()