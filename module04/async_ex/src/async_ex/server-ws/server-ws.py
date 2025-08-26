import websockets
import asyncio
from faker import Faker


fake = Faker()

class Server:
    clients = set()

    async def register(self, client):
        client.name = fake.name()
        self.clients.add(client)
        print(f"{client.remote_address} connects")

    async def unregister(self, client):
        self.clients.remove(client)
        print(f"{client.remote_address} removed")

    async def ws_handler(self, ws):
        await self.register(ws)
        try:
            await self.notify(ws)
        except:
            await self.unregister(ws)

    async def send_message(self, message):
        if self.clients:
            [await client.send(message) for client in self.clients]


    async def notify(self, ws):
        async for message in ws:
            await self.send_message(f"{ws.name}: {message}")        


server = Server()

async def main():
    async with websockets.serve(server.ws_handler, "localhost", "8080"):
        await asyncio.Future() # run foreve


asyncio.run(main())