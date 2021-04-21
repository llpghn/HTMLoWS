import asyncio
import websockets
import json

# Imports of Components
from server.components.components import greeting
from server.components.components import main
from server.components.components import input_temp_preference

# Custom-Imports
from server import constants
from server.store import Store


"""
--> {"func": "<PROCEDURE_NAME>", "id": <ID>, "payload": {<DICTIONARY>}}
<-- {"parent": "<DOM-PARENT-ELEMENT>", "id": <ID>, "html": "<HTML>"}
"""

class Server:
    def __init__(self, store):
        self.store = store

    def get_port(self):
        #return os.getenv('WS_PORT', '8765')
        return constants.SERVER_BINDING_PORT

    def get_host(self):
        #return os.getenv('WS_HOST', 'localhost')
        return constants.SERVER_BINDING_INTERFACE

    def start(self):
        return websockets.serve(self.handler, self.get_host(), self.get_port())

    async def handler(self, websocket, path):
        async for message in websocket:
            print('server received :', message)
            #await websocket.send(message)
            data = json.loads(message)

            if data['func'] in constants.PROCEDURES:

                if data['func'] == 'MAIN':
                    print('> Greeting Message erhalten. > ' + message)
                    response_dict = {
                        'parent': "root",
                        'id': data['id'],
                        'html': main(self.store.getall())
                    }
                    await websocket.send(json.dumps(response_dict))

                elif data['func'] == 'SHOW_VIEW_ADD_PREFERENCE':
                    print('> SHOW_VIEW_ADD_PREFERENCE > ' + message)
                    if data['payload']:
                        # Wir haben Payload enthalten, was machen wir nun damit?
                        print(f'> > {data["payload"]}')
                        for k in data['payload'].keys():
                            self.store.set(k, data['payload'][k])
                            print('> > > k: ' + k + ' - v: ' + data['payload'][k])
                    response_dict = {
                        'parent': "content",
                        'id': data['id'],
                        'html': input_temp_preference(self.store.getall())
                    }
                    await websocket.send(json.dumps(response_dict))
                """
                elif data['func'] == 'LISTE':
                    print('> Laden der Liste > ' + message)
                    response_dict = {
                        'parent': "liste",
                        'id': data['id'],
                        'html': greeting(["Alpha", "Beta", "Gamma"])
                    }
                    await websocket.send(json.dumps(response_dict))
                """
    def get_dom(self):
        return


if __name__ == '__main__':
    store = Store()
    store.set('temperature', 20)
    store.set('humidity', 45.5)

    ws = Server(store)
    asyncio.get_event_loop().run_until_complete(ws.start())
    asyncio.get_event_loop().run_forever()