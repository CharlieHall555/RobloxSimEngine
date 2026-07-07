import asyncio

# A simple Job wrapper
class Job:
    def __init__(self, code: str):
        self.code = code
        self.result = None
        self.event = asyncio.Event()