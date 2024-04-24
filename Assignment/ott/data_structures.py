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
        }

    @staticmethod
    def prepare(json):
        ip = json["ip"]
        port = json["port"]
        name = json["name"]
        return MutexNode(ip=ip, port=port, name=name)


class MutexMessage:
    def __init__(self, type, node, msg, file_name, timestamp):
        self.msg = msg
        self.msg_type = type
        self.node = node
        self.file_name = file_name
        self.timestamp = timestamp

    @staticmethod
    def prepare(json):
        file_name = json["file_name"]
        msg = json["msg"]
        msg_type = json["msg_type"]
        timestamp = json["timestamp"]
        node = MutexNode.prepare(json=json["node"])
        return MutexMessage(
            msg=msg, node=node, type=msg_type, file_name=file_name, timestamp=timestamp
        )

    def to_json(self):
        return {
            "msg": self.msg,
            "timestamp": self.timestamp,
            "msg_type": self.msg_type,
            "file_name": self.file_name,
            "node": self.node.to_json(),
        }
