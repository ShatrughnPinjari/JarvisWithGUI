# Import module
import sqlite3

def add_data(query):
    conn = sqlite3.connect('../Data/chats.db')
    cursor = conn.cursor()
    table = "INSERT INTO ASSISTANT(QUERY, DATE_TIME) VALUES (?, datetime('now', 'localtime'))"
    cursor.execute(table, (query,))
    conn.commit()
    conn.close()
    return True

def get_data():
    conn = sqlite3.connect('../Data/chats.db')
    cursor = conn.cursor()
    data = cursor.execute('SELECT * FROM ASSISTANT')
    table_head = [column[0] for column in data.description]
    
    print("{:<14} {:<79} {:<20}".format(table_head[0], table_head[1], table_head[2]))
    print()
    
    for row in data:
        print("{:<14} {:<79} {:<20}".format(row[0], row[1], row[2]))
    
    conn.close()