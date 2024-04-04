import os
import time
import mysql.connector
import mysql
import logging
from DbHandler import DbHandler
from WebSocketHandler import WebSocketHandler, WebSocketObserver, WebSocketStatus

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)


class Controller(WebSocketObserver):

    __webSocket = None
    __dbHandler = None

    def __init__(self):
        self.db_connect()
        self.__webSocket = WebSocketHandler(url=os.getenv('WEBSOCKET_URL'))
        self.__webSocket.attach(self)
        self.__webSocket.run()

    def db_connect(self):
        try:
            logging.info("Try connect to DataBase.")
            self.__dbHandler = DbHandler(
                db_name=os.getenv('MYSQL_DATABASE'),
                user_name=os.getenv('MYSQL_USER'),
                user_pass=os.getenv('MYSQL_PASSWORD'),
                values_tab_name=os.getenv('MYSQL_TABLE_NAME')
            )
            self.__dbHandler.connect()
            logging.info("DataBase connected!")

        except mysql.connector.Error as err:
            logging.error(f"DataBase connector error: {err.errno} {err.msg}")
            time.sleep(3)
            self.db_connect()
        except Exception as err:
            logging.error(f"DataBase Exception: {str(err)}")
            time.sleep(3)
            self.db_connect()

    def update(self, data) -> None:
        if data.status == WebSocketStatus.OK:
            if len(data.counters_data) > 0:
                try:
                    self.__dbHandler.add_counters_data(data.counters_data)

                except mysql.connector.Error as err:
                    logging.error(f"DataBase: {err.errno} {err.msg}")
                    self.db_connect()

        elif data.status == WebSocketStatus.CONNECTING:
            logging.info("Try connect to WebSocket...")
        elif data.status == WebSocketStatus.CONNECTED:
            logging.info("WebSocket connected!")
        elif data.status == WebSocketStatus.ERROR:
            logging.error(f"WebSocket: {data.error_msg}")
            self.__webSocket.stop()
            time.sleep(3)
            self.__webSocket.run()

