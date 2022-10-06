import logging
import pprint
import threading
import time
from pprint import pformat

from node_socket import UdpSocket


class Order:
    RETREAT = 0
    ATTACK = 1


class General:

    def __init__(self, my_id: int, is_traitor: bool, my_port: int,
                 ports: list, node_socket: UdpSocket, city_port: int):
        self.my_id = my_id
        self.city_port = city_port
        self.node_socket = node_socket
        self.my_port = my_port
        self.is_traitor = is_traitor
        self.orders = []

        self.general_port_dictionary = {}
        for i in range(0, 4):
            self.general_port_dictionary[i] = ports[i]
        logging.debug(f"self.general_port_dictionary: {pformat(self.general_port_dictionary)}")

        self.port_general_dictionary = {}
        for key, value in self.general_port_dictionary.items():
            self.port_general_dictionary[value] = key
        logging.debug(f"self.port_general_dictionary: {pprint.pformat(self.port_general_dictionary)}")

    def start(self):
        logging.info("Start listening for incoming messages...")
        for i in range(3):
            incoming_message: list = self.listen_procedure()
            sender = incoming_message[0]
            logging.info(f"Got incoming message from {sender}: {incoming_message}")

            order = int(incoming_message[1].split("=")[1])
            self.orders.append(order)
            logging.info(f"Append message to a list: {pformat(self.orders)}")

            self.sending_procedure(sender, order)

        self.conclude_action(self.orders)

    def _most_common(self, lst):
        return max(set(lst), key=lst.count)

    def listen_procedure(self):
        input_value, address = self.node_socket.listen()
        logging.debug(f"input_value: {input_value}")
        logging.debug(f"address: {address}")
        incoming_message: list = input_value.split("~")
        return incoming_message

    def sending_procedure(self, sender, order):
        if sender == "supreme_general":
            logging.info("Send supreme general order to other generals with threading...")
            if self.is_traitor:
                order = Order.ATTACK if order == Order.RETREAT else Order.RETREAT
            message = f"general_{self.my_id}~order={order}"
            logging.info(f"message: {message}")
            for other_general_port, value in self.port_general_dictionary.items():
                if value == 0:
                    continue
                if other_general_port == self.my_port:
                    continue
                logging.info("Initiate threading to send the message...")
                thread = threading.Thread(target=self.node_socket.send,
                                          args=(message, other_general_port))
                logging.info("Start threading...")
                thread.start()
                logging.info(f"Done sending message "
                             f"to general {self.port_general_dictionary[other_general_port]}...")
            return message

    def conclude_action(self, orders):
        logging.info("Concluding action...")
        logging.debug(f"is_traitor: {self.is_traitor}")
        if self.is_traitor:
            logging.info("I am a traitor...")
            return None
        else:
            order = self._most_common(orders)
            action = "ATTACK" if order else "RETREAT"
            logging.info(f"action: {action}")
            message = f"general_{self.my_id}~action={order}"
            logging.debug(f"self.city_port: {self.city_port}")
            self.node_socket.send(message, self.city_port)
            logging.info("Done doing my action...")
        return message


class SupremeGeneral(General):

    def __init__(self, my_id: int, is_traitor: bool, my_port: int, ports: list, node_socket: UdpSocket, city_port: int,
                 order: Order):
        super().__init__(my_id, is_traitor, my_port, ports, node_socket, city_port)
        self.order = order
        logging.debug(f"city_port: {city_port}")

    def sending_procedure(self, sender, order):
        result = []
        message = f"{sender}~order="
        for i in range(1, len(self.port_general_dictionary)):
            general_port = self.general_port_dictionary[i]
            logging.debug(f"my_port: {self.my_port}")
            logging.debug(f"general_port: {general_port}")
            logging.info(f"Send message to general {i} with port {general_port}")
            if self.is_traitor:
                order = Order.RETREAT if i % 2 == 0 else Order.ATTACK
            result.append(order)
            message_send = f"{message}{order}"
            self.node_socket.send(message_send, general_port)
        logging.info("Finish sending message to other generals...")
        return result

    def start(self):
        logging.info("Supreme general is starting...")
        logging.info("Wait until all generals are running...")
        time.sleep(0.1)
        result = self.sending_procedure("supreme_general", self.order)

        self.conclude_action(result)

    def conclude_action(self, orders):
        logging.info("Concluding action...")
        if self.is_traitor:
            logging.info("I am a traitor...")
            return
        elif self.order:
            logging.info("ATTACK the city...")
        else:
            logging.info("RETREAT from the city...")

        logging.info("Send information to city...")
        message = f"supreme_general~action={self.order}"
        logging.debug(f"message: {message}")
        logging.debug(f"self.city_port: {self.city_port}")
        self.node_socket.send(message, self.city_port)
        logging.info("Done sending information...")
        return message


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
