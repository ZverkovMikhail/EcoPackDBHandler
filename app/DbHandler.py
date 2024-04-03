import time
import mysql.connector
from mysql.connector import errorcode


class DbHandler:
    __db_connection = None
    db_name = None
    user_name = None
    user_pass = None
    values_tab_name = None

    def __init__(self, db_name, user_name, user_pass, values_tab_name):
        self.db_name = db_name
        self.user_name = user_name
        self.user_pass = user_pass
        self.values_tab_name = values_tab_name

    def connect(self):
        self.__connect()
        self.__create_table()

    def disconnect(self):
        self.__db_connection.close()

    def __create_table(self):
        try:
            cursor = self.__db_connection.cursor()
            cursor.execute("SELECT * FROM %s" % self.values_tab_name)
            cursor.fetchall()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_NO_SUCH_TABLE:
                sql = ("CREATE TABLE `%s` ("
                       "  `modbus_id` tinyint unsigned,"
                       "  `name` varchar(50),"
                       "  `value` mediumint unsigned,"
                       "  `status` varchar(50),"
                       "  `plan` mediumint unsigned,"
                       "  `production` mediumint unsigned,"
                       "  `performance` mediumint unsigned,"
                       "  PRIMARY KEY (`modbus_id`))" % self.values_tab_name
                       )
                cursor.execute(sql)
            else:
                raise mysql.connector.Error(err.msg, err.errno, err.sqlstate)

    def __delete_not_used(self, counters_data):
        get_ids_sql = f"SELECT modbus_id FROM {self.values_tab_name}"
        cursor = self.__db_connection.cursor()
        cursor.execute(get_ids_sql)
        results = cursor.fetchall()
        if not results:
            return
        db_ids = set(set(list(zip(*results))[0]))
        ws_ids = set([c['id'] for c in counters_data])
        unused = list([[s] for s in list(db_ids - ws_ids)])
        if unused:
            sql = f"DELETE FROM {self.values_tab_name} WHERE modbus_id = %s"
            cursor.executemany(sql, unused)

    def add_counters_data(self, counters_data):
        vals = []
        cursor = self.__db_connection.cursor()
        for counter_data in counters_data:
            vals.append(
                (
                    counter_data['id'],
                    counter_data['title'],
                    counter_data['value'],
                    counter_data['status'],
                    counter_data['plan'],
                    counter_data['production'],
                    counter_data['performance']
                )
            )
        replace_sql = (
            f"REPLACE INTO {self.values_tab_name} "
            "(modbus_id, name, value, status, plan, production, performance) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        self.__delete_not_used(counters_data)
        cursor.executemany(replace_sql, vals)
        self.__db_connection.commit()

    def __connect(self):

        self.__db_connection = mysql.connector.connect(
            user=self.user_name, password=self.user_pass,
            host='mysql',
            database=self.db_name
        )
