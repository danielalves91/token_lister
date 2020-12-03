import sqlite3
import httpx

conn = sqlite3.connect('coinbase.db', check_same_thread=False)
c = conn.cursor()

# c.execute("""CREATE TABLE coinbase_pro (
#             name text,
#             id text,
#             active integer,
#             UNIQUE(name, id)
#             )""")

# c.execute("""CREATE TABLE acdx (
#             name text,
#             id text,
#             active integer,
#             UNIQUE(name, id)
#             )""")

# c.execute("""CREATE TABLE binance (
#             name text,
#             id text,
#             active integer,
#             UNIQUE(name, id)
#             )""")

def insert_token(token_name, symbol, table):
    with conn:
        c.execute(f"INSERT OR IGNORE INTO {table} VALUES (:name, :id, :active)", {"name":token_name, "id":symbol, "active":1})


def delete_token(symbol, table):
    with conn:
        c.execute(f"SELECT name FROM {table} WHERE active = :active", 
                    {"active": 0})

        data = c.fetchone()
        if data:
            c.execute(f"DELETE FROM {table} WHERE active = :active", 
            {"active": 0})

            return data

def check_api(req, table, api_elements):
    with conn:
        c.execute(f"UPDATE {table} SET active = :active", {'active': 0})
        for token in req:
            c.execute(f"""UPDATE {table} SET active = :active
                        WHERE id = :id""", {'id': token[api_elements['id']], 'active': 1})

            c.execute(f"SELECT name FROM {table} WHERE id = :id",
                        {'id': token[api_elements['id']]})

            data = c.fetchone()
            
            if data is None:
                insert_token(token[api_elements['name']], token[api_elements['id']], table)
                return token[api_elements['name']], token[api_elements['id']]
            else:
                continue
