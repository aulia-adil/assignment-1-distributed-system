import logging
import threading
from pprint import pformat

from node_socket import UdpSocket


class Order:
    RETREAT = 0
    ATTACK = 1


class General:

    def __init__(self, my_id: int, is_traitor: bool, my_port: int,
                 ports: list, node_socket: UdpSocket, city_port: int):
        self.ports = ports
        self.my_id = my_id
        self.city_port = city_port
        self.node_socket = node_socket
        self.my_port = my_port
        self.is_traitor = is_traitor

    def start(self):
        """
        TODO
        :return: None
        """
        return

    def listen_procedure(self):
        """
        TODO
        :return: list
        """
        return list()

    def sending_procedure(self, sender, order):
        """
        TODO
        :param sender: sender id
        :param order: order
        :return: str or None
        """
        return "" or None

    def conclude_action(self, orders):
        """
        TODO
        :param orders: list
        :return: str or None
        """
        return "" or None


class SupremeGeneral(General):

    def __init__(self, my_id: int, is_traitor: bool, my_port: int, ports: list, node_socket: UdpSocket, city_port: int,
                 order: Order):
        super().__init__(my_id, is_traitor, my_port, ports, node_socket, city_port)
        self.order = order

    def sending_procedure(self, sender, order):
        """
        TODO
        :param sender: sender id
        :param order: order
        :return: list
        """
        return []

    def start(self):
        """
        TODO
        :return: None
        """
        return None

    def conclude_action(self, orders):
        """
        TODO
        :param orders: list
        :return: str or None
        """
        return "" or None


def thread_exception_handler(args):
    logging.error(f"Uncaught exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def main(is_traitor: bool, node_id: int, ports: list,
         my_port: int = 0, order: Order = Order.RETREAT,
         is_supreme_general: bool = False, city_port: int = 0):
    threading.excepthook = thread_exception_handler
    try:
        if node_id > 0:
            logging.info(f"General {node_id} is running...")
        else:
            logging.info("Supreme general is running...")
        logging.debug(f"is_traitor: {is_traitor}")
        logging.debug(f"ports: {pformat(ports)}")
        logging.debug(f"my_port: {my_port}")
        logging.debug(f"order: {order}")
        logging.debug(f"is_supreme_general: {is_supreme_general}")
        logging.debug(f"city_port: {city_port}")

        if node_id == 0:
            obj = SupremeGeneral(my_id=node_id,
                                 city_port=city_port,
                                 is_traitor=is_traitor,
                                 node_socket=UdpSocket(my_port),
                                 my_port=my_port,
                                 ports=ports, order=order)
        else:
            obj = General(my_id=node_id,
                          city_port=city_port,
                          is_traitor=is_traitor,
                          node_socket=UdpSocket(my_port),
                          my_port=my_port,
                          ports=ports, )
        obj.start()
    except Exception:
        logging.exception("Caught Error")
        raise
