import sqlite3

db_name = 'car_wash.db'

def make_bd():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS car_wash(
                    wash_id INT PRIMARY KEY,
                    wash_name TEXT,
                    wash_cord TEXT,
                    open_time TEXT,
                    close_time TEXT,
                    free_time TEXT)''')
    con.commit()
    con.close()

def check_car_wash(wash_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute(f'''SELECT wash_id FROM car_wash WHERE wash_id = {int(wash_id)}''')
    status = cur.fetchone()
    con.commit()
    con.close()
    if status is not None:
        return True
    else:
        return False

def add_car_wash(wash_id, name, coords, open_time='9:00', close_time='23:00', free_time='9:00'):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute("INSERT INTO car_wash(wash_id, wash_name, wash_cord, open_time, close_time, free_time) VALUES(?, ?, ?, ?, ?, ?)", (
        int(wash_id),
        name,
        coords,
        open_time,
        close_time,
        free_time
    ))
    con.commit()
    con.close()

def time_by_id(wash_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute(f'''SELECT open_time, close_time, free_time FROM car_wash WHERE wash_id = {wash_id}''')
    result = cur.fetchone()
    con.commit()
    con.close()
    return result

def update_time_by_id(wash_id, new_time):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    query = "UPDATE car_wash SET free_time = '{0}' WHERE wash_id = '{1}'".format(str(new_time), int(wash_id))

    cur.execute(query)
    con.commit()
    con.close()

def get_info_about(wash_id):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute(f'''SELECT wash_id, wash_name, wash_cord, free_time FROM car_wash WHERE wash_id = {wash_id}''')
    result = cur.fetchone()
    con.commit()
    con.close()
    return result