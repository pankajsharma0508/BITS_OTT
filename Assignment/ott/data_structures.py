import json


class ListNode:
    def __init__(self, ip, cost):
        self.ip = ip
        self.cost = cost
        self.next = None


class ServerLinkedList:
    def __init__(self, replica_servers):
        self.head = None
        rserver_ip = replica_servers.split(",")
        for ip in rserver_ip:
            if ip != "":
                self.insert(ip, 1)

    def insert(self, ip, cost):
        new_node = ListNode(ip, cost)
        if self.head is None or cost < self.head.cost:
            new_node.next = self.head
            self.head = new_node
        else:
            current = self.head
            while current.next and current.next.cost < cost:
                current = current.next
            new_node.next = current.next
            current.next = new_node

    def display(self):
        current = self.head
        while current:
            print(f"IP: {current.ip}, Cost: {current.cost}")
            current = current.next


class MutexNode:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.address = f"{ip}:{port}"

    def to_json(self):
        return {
            "ip": self.ip,
            "port": self.port,
            "name": self.name,
            "address": self.address,
        }


class MutexMessage:
    def __init__(self, type, node, msg):
        self.msg = msg
        self.msg_type = type
        self.node = node

    def to_json(self):
        json_string = {
            "msg": self.msg,
            "msg_type": self.msg_type,
            "node": self.node.to_json(),
        }
        return json_string.encode("utf-8")
