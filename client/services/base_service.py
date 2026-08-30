from abc import ABC

from client.client import Client


class BaseService(ABC):
    def __init__(self, client: Client):
        self.client = client