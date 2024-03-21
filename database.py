import sqlite3


class DB:
    def __init__(self, file) -> None:
        self.conn = sqlite3.connect(file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def check_user_in_db(self, input_user_id):
        res = self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (input_user_id,)
        )
        return bool(len(res.fetchall()))

    def get_user_id(self, input_user_id):
        res = self.cursor.execute(
            "SELECT id FROM users WHERE user_id = ?", (input_user_id,)
        )
        return res.fetchone()[0]

    def add_user(self, input_user_id, home_port="MOW"):
        self.cursor.execute(
            "INSERT INTO users ('user_id','home_airport','is_admin') VALUES(?,?,?)",
            (input_user_id, home_port, 0),
        )
        return self.conn.commit()

    def change_airport(self, input_user_id, new_port):
        self.cursor.execute(
            "UPDATE users SET ('home_airport') = ? WHERE id = ?",
            (
                new_port,
                self.get_user_id(input_user_id),
            ),
        )
        return self.conn.commit()

    def add_flight(
        self, user_id, port_from, port_to, input_price, departure, airline, time
    ):
        self.cursor.execute(
            "INSERT INTO flights_search ('user_id','airport_from','airport_to','price','dep_date','airline','search_time') VALUES(?,?,?,?,?,?,?)",
            (user_id, port_from, port_to, input_price, departure, airline, time),
        )
        return self.conn.commit()

    def get_home_airport(self, input_user_id):
        res = self.conn.execute(
            "SELECT home_airport FROM users WHERE id = ?",
            (self.get_user_id(input_user_id),),
        )
        return res.fetchall()[0][0]

    def show_user_flights(self, user_id):
        res = self.cursor.execute(
            "SELECT airport_from,airport_to,price,dep_date,airline FROM flights_search WHERE user_id = ? ORDER BY search_time DESC  LIMIT 10",
            (user_id,),
        )
        return res.fetchall()

    def count_user_searches(self, user_id):
        res = self.cursor.execute(
            "SELECT COUNT(*) FROM flights_search WHERE user_id = ?", (user_id)
        )
        return res.fetchall()

    def get_all_users(self):
        res = self.cursor.execute("SELECT DISTINCT user_id from users")
        return res.fetchall()

    def check_admin(self):
        res = self.cursor.execute(
            "SELECT user_id FROM users WHERE is_admin = 1",
        )
        return res.fetchall()[0][0]
