import enum
import json
import traceback
from abc import abstractmethod
from typing import List

import websockets
from websockets.sync.client import connect


class WebSocketStatus(enum.IntEnum):
    CONNECTING = 1
    CONNECTED = 2
    OK = 3
    ERROR = 4


class WebSocketData:
    counters_data = None
    status = None
    error_msg = None

    def __init__(self, counters_data=None, status=WebSocketStatus.OK, error_msg=''):
        if counters_data is None:
            counters_data = []
        self.counters_data = counters_data
        self.status = status
        self.error_msg = error_msg


class WebSocketObserver:
    @abstractmethod
    def update(self, data: WebSocketData) -> None:
        pass


class WebSocketHandler:
    __ws_url = None
    __is_run = True
    __observers: List[WebSocketObserver] = []

    def __init__(self, url):
        self.__ws_url = url

    def run(self):
        try:
            self.__is_run = True
            self.notify(WebSocketData(status=WebSocketStatus.CONNECTING))
            with connect(self.__ws_url) as websocket:
                self.notify(WebSocketData(status=WebSocketStatus.CONNECTED))
                while self.__is_run:
                    message = websocket.recv()
                    counters_data = json.loads(message)
                    self.notify(WebSocketData(counters_data=counters_data))
        except websockets.exceptions.ConnectionClosedError as err:
            self.notify(WebSocketData(status=WebSocketStatus.ERROR, error_msg=f'{err.code}: {str(err)}'))
        except ConnectionRefusedError as err:
            self.notify(WebSocketData(status=WebSocketStatus.ERROR, error_msg=f'{err.errno}: {err.strerror}'))
        except ConnectionError as err:
            self.notify(WebSocketData(status=WebSocketStatus.ERROR, error_msg=f'WebSocket Connection: {str(err)}'))
        except Exception as err:
            self.notify(WebSocketData(status=WebSocketStatus.ERROR,
                                      error_msg=f'WebSocket Exception: {str(err)} {traceback.format_exc()}'))

    def stop(self):
        self.__is_run = False

    def attach(self, observer: WebSocketObserver) -> None:
        self.__observers.append(observer)

    def detach(self, observer: WebSocketObserver) -> None:
        self.__observers.remove(observer)

    def notify(self, data: WebSocketData) -> None:
        for observer in self.__observers:
            observer.update(data)
