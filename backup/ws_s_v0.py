#!/usr/bin/env python

import asyncio
import websockets
import json

from server import constants

"""
--> {"func": "<PROCEDURE_NAME>", "id": <ID>, "payload": {<DICTIONARY>}}
<-- {"parent": "<DOM-PARENT-ELEMENT>", "id": <ID>, "html": "<HTML>"}
"""


async def root(websocket, path):
    while True:
        msg = await websocket.recv()
        print("--> " + msg)
        msg_json = json.loads(msg)

        if msg_json['func'] == 'GREETING':
            print(" GREETING")
            response = {
                'parent': "root",
                'id': -1,
                'html': '<div id="romeo">Hello Holy Molly.</div>'
            }
            print("<-- " + str(response))
            await websocket.send(response)


print("Start HTMLoWS-Server 1.0.00")
start_server = websockets.serve(root, constants.SERVER_BINDING_INTERFACE, constants.SERVER_BINDING_PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()