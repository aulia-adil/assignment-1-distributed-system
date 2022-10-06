import unittest
from unittest.mock import patch

from main import execution
from node import Order, General, SupremeGeneral
from node_socket import UdpSocket
from tests.public_test import BgpTest


class BgpHiddenTest(BgpTest):

    def setUp(self) -> None:
        super().setUp()
        self.traitor_general = General(
            my_id=2, is_traitor=True,
            my_port=1, ports=[0, 1, 2, 3],
            node_socket=UdpSocket(),
            city_port=0
        )
        self.traitor_supreme_general = SupremeGeneral(
            my_id=3, is_traitor=True,
            my_port=0, ports=[0, 1, 2, 3],
            node_socket=UdpSocket(),
            city_port=0,
            order=Order.ATTACK
        )


    def test_send_procedure_traitor_return_message(self):
        order = Order.ATTACK
        result = self.traitor_general.sending_procedure("supreme_general", order)
        expected = f"general_{self.traitor_general.my_id}~order={Order.RETREAT}"
        self.assertEqual(expected, result)

    def test_send_procedure_traitor_sg_return_list(self):
        order = Order.ATTACK
        result = self.traitor_supreme_general.sending_procedure("supreme_general", order)
        expected = [Order.ATTACK, Order.RETREAT, Order.ATTACK]
        self.assertEqual(expected, result)

    def test_send_procedure_traitor_sg_return_list1(self):
        order = Order.RETREAT
        result = self.traitor_supreme_general.sending_procedure("supreme_general", order)
        expected = [Order.ATTACK, Order.RETREAT, Order.ATTACK]
        self.assertEqual(expected, result)

    def test_concluding_action_traitor_return_none(self):
        result = self.traitor_general.conclude_action([Order.ATTACK, Order.RETREAT, Order.ATTACK])
        expected = None
        self.assertEqual(expected, result)

    def test_concluding_action_traitor_sg_return_none(self):
        result = self.traitor_supreme_general.conclude_action(Order.ATTACK)
        expected = None
        self.assertEqual(expected, result)

    def test_city1(self):
        temp = [
            # ("general_1~order=1", ("localhost", 123)),
            ("supreme_general~order=0", ("localhost", 123)),
            ("general_2~order=1", ("localhost", 123)),
            ("general_3~order=0", ("localhost", 123)),
        ]
        self.mock_incoming_message.side_effect = temp
        self.city.number_general = len(temp)
        result = self.city.start()
        expected = "FAILED"
        self.assertEqual(expected, result)

    def test_city2(self):
        temp = [
            # ("general_1~order=1", ("localhost", 123)),
            ("supreme_general~order=0", ("localhost", 123)),
            # ("general_2~order=1", ("localhost", 123)),
            ("general_3~order=0", ("localhost", 123)),
        ]
        self.mock_incoming_message.side_effect = temp
        self.city.number_general = len(temp)
        result = self.city.start()
        expected = C.R
        self.assertEqual(expected, result)

    def test_city3(self):
        temp = [
            ("general_1~order=1", ("localhost", 123)),
            # ("supreme_general~order=0", ("localhost", 123)),
            ("general_2~order=1", ("localhost", 123)),
            # ("general_3~order=0", ("localhost", 123)),
        ]
        self.mock_incoming_message.side_effect = temp
        self.city.number_general = len(temp)
        result = self.city.start()
        expected = C.A
        self.assertEqual(expected, result)

    def test_city4(self):
        temp = []
        self.mock_incoming_message.side_effect = temp
        self.city.number_general = len(temp)
        result = self.city.start()
        expected = C.E
        self.assertEqual(expected, result)

class C:
    R = "RETREAT"
    A = "ATTACK"
    F = "FAILED"
    E = "ERROR_LESS_THAN_TWO_GENERALS"
    t = True
    f = False

class BgpHiddenGrader(unittest.TestCase):

    def test1(self):
        result = execution([False, True, True, False], C.R)
        expected = C.F
        self.assertEqual(expected, result)

    def test2(self):
        result = execution([True, False, False, False], C.R)
        expected = C.A
        self.assertEqual(expected, result)

    def test3(self):
        result = execution([False, True, True, True], C.A)
        expected = C.E
        self.assertEqual(expected, result)

    def test4(self):
        result = execution([False, False, False, False], C.A)
        expected = C.A
        self.assertEqual(expected, result)

    def test5(self):
        result = execution([C.f,C.f,C.f,C.f], C.A)
        expected = C.A
        self.assertEqual(expected, result)

    def test6(self):
        result = execution([True, False, False, False], C.A)
        expected = C.A
        self.assertEqual(expected, result)

    def test7(self):
        result = execution([C.f, C.f, C.f, C.t], C.R)
        expected = C.R
        self.assertEqual(expected, result)

    def test8(self):
        result = execution([C.f, C.f, C.t, C.f], C.A)
        expected = C.A
        self.assertEqual(expected, result)

    def test9(self):
        result = execution([C.f, C.t, C.t, C.f], C.R)
        expected = C.F
        self.assertEqual(expected, result)

    def test10(self):
        result = execution([C.f, C.t, C.t, C.t], C.R)
        expected = C.E
        self.assertEqual(expected, result)

    def test11(self):
        result = execution([C.t, C.t, C.t, C.t], C.R)
        expected = C.E
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
