import sqlite3
conn = sqlite3.connect('C:/Users/HP/Downloads/Nutriscan/Nutriscan/nutri_project/db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Number of tables:', len(tables))
print('Tables:')
for table in tables:
    print('-', table[0])
conn.close()