import ast
import logging
import math
import pprint
import random
import sys
import threading
import time
import traceback
from argparse import ArgumentParser
import socket
from ast import literal_eval
from pprint import pformat
import csv

from node import Order
from node_socket import UdpSocket


class City:

    def __init__(self, my_port: int, number_general: int) -> None:
        self.number_general = number_general
        self.my_port = my_port
        self.node_socket = UdpSocket(my_port)

    def start(self):
        logging.info("Listen to incoming messages...")
        status = []
        for i in range(self.number_general):
            message, address = self.node_socket.listen()
            general = message.split("~")[0]
            action = int(message.split("~")[1].split("=")[1])
            status.append(action)
            if action == Order.RETREAT:
                action = "RETREAT"
                message = f"{general} {action} from us!"
            else:
                action = "ATTACK"
                message = f"{general} {action} us!"
            logging.info(message)
        logging.info("Concluding what happen...")
        logging.debug(f"status: {status}")
        retreat_counter = 0
        attack_counter = 0
        result_list_length = len(status)
        for i in status:
            if 1 == i:
                attack_counter += 1
            else:
                retreat_counter += 1
        general_consensus = "FAILED"
        if result_list_length < 2:
            general_consensus = "ERROR_LESS_THAN_TWO_GENERALS"
        elif attack_counter == result_list_length:
            general_consensus = "ATTACK"
        elif retreat_counter == result_list_length:
            general_consensus = "RETREAT"
        result = f"GENERAL CONSENSUS: {general_consensus}"
        logging.info(result)
        return general_consensus


def thread_exception_handler(args):
    logging.error(f"Uncaught exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def main(city_port: int, number_general: int):
    threading.excepthook = thread_exception_handler
    try:
        logging.debug(f"city_port: {city_port}")
        logging.info(f"City is running...")
        logging.info(f"Number of loyal general: {number_general}")
        city = City(my_port=city_port, number_general=number_general)
        return city.start()

    except Exception:
        logging.exception("Caught Error")
        raise
