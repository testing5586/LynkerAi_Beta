import sqlite3
from datetime import datetime

# Database connection
connection = sqlite3.connect('ziwei_database.db')
cursor = connection.cursor()

# Insert function
def insert_mingzhu(name, gender, birth_time, ziwei_palace, main_star, shen_palace):
    insert_query = '''
    INSERT INTO mingzhu (name, gender, birth_time, ziwei_palace, main_star, shen_palace)
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, (name, gender, birth_time, ziwei_palace, main_star, shen_palace))
    connection.commit()

# Insert the given Mingzhu record
name = '命主C'
gender = '女'
birth_time = datetime.strptime('1990-05-20T15:30:00', '%Y-%m-%dT%H:%M:%S')
ziwei_palace = '巳'
main_star = '廉贞'
shen_palace = '卯'

insert_mingzhu(name, gender, birth_time, ziwei_palace, main_star, shen_palace)

# Close the database connection
connection.close()