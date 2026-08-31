from client.client import Client


class BaseService:
    def __init__(self, client: Client):
        self.client = client