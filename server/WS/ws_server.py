import socket
import logging # Logging
import os
import select

import hashlib # Used in create websocket upgrade message
import base64 # Used in create websocket upgrade message

from server.WS.ws_rec_msg import WSRecMessage
from server.WS.LogicProcessor.LogicProcessor import LogicProcessor

class WSServer():
    def __init__(self, logger, configuration):
        self.configuration = configuration
        self.logger = logger
        self.configuration = configuration
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((configuration['interface'], configuration['port']))
        self.socket.listen(5)
        self.socket_read_list = [self.socket]    # Class
        self.client_sockets = [] # Liste mit den entsprechenden Clients
        self.transaction_id = 0

    def set_logic_processor(self, processor):
        """ Setzt den Handler der aufgerufen wird, wenn eine Nachricht erhalten worden ist.
            Von diesem wird dann die Methode handle auferufen. """
        self.logic_processor = processor



    def start_listen(self):
        """ Beginnt das lauschen auf Daten auf den entsprechenden Port und bearbeitet dann die Daten. """
        while True:
            readable, writable, errored = select.select(self.socket_read_list, [], [])
            for s in readable:
                # Generiere eine Transaktion ID
                self.transaction_id += 1
                if self.transaction_id > 99:
                    self.transaction_id = 0

                response = None
                frame = None
                # Behandle die Socket-Änderung
                if s is self.socket:
                    # Bearbeite neue Verbindungsanfragen von Clients
                    client_socket, address = self.socket.accept()
                    self.socket_read_list.append(client_socket)
                    self.logger.debug(str(self.transaction_id) + " Connection from" + str(address))
                    self.client_sockets.append({
                        'raddr': client_socket.getsockname(),
                        'level': 'HTTP', # HTTP, WS
                        'msg': None
                    })
                else:
                    self.logger.debug(str(self.transaction_id) + " Receiving Message from " + str(s))

                    # Lesen der Nachricht
                    frame = s.recv(self.configuration['mtu'])

                    # START: Finde den index für den zu behandelnenden Index um den es sich handelt.
                    index_of_current_socket = -1
                    idx = 0
                    for cs in self.client_sockets:
                        if cs['raddr'] == client_socket.getsockname():
                            index_of_current_socket = idx
                            break
                        idx += 1
                    self.logger.debug(str(self.transaction_id) + " Found Socket at index: " + str(index_of_current_socket))
                    self.logger.debug(str(self.transaction_id) + " \tSocket-Level: " + self.client_sockets[index_of_current_socket]['level'])
                    # ENDE

                    # Bearbeite den Socket abhängig vom Status HTTP oder WS
                    # Neuer TCP Socket mit HTTP Protokoll
                    if self.client_sockets[index_of_current_socket]['level'] == 'HTTP':
                        self.logger.debug("Received ")
                        decoded_frame = frame.decode('utf-8')
                        # Prüfen ob die Socketverbindung ge-upgraded werden soll
                        if decoded_frame.find("Connection: Upgrade") > -1 and decoded_frame.find("Upgrade: websocket") >= -1:
                            self.logger.debug("Upgrade Socket Connection detected")
                            res_msg_str = self.get_response_socket_upgrade(decoded_frame)
                            self.logger.debug("Response Message: " + res_msg_str)
                            s.send(bytes(res_msg_str, "utf-8"))
                            self.client_sockets[index_of_current_socket]['level'] = "WS"
                            break
                        else:
                            s.close()

                    # Socket wurde zum Websocket geupgraded und daher haben wir nun eine vollwertige
                    # WebSocket-Verbindug die wie eine solche behandelt werden muss.
                    elif self.client_sockets[index_of_current_socket]['level'] == 'WS':
                        self.logger.debug(str(self.transaction_id) + " Received WS Message")

                        ws_rec_msg = WSRecMessage()
                        ws_rec_msg.set_frame(frame)
                        ws_rec_msg.frame_to_msg()
                        res = None

                        # Behandlung der Standardnachrichten
                        if ws_rec_msg.is_ping_frame():
                            self.logger.debug("Received Ping - Sending Pong")


                        elif ws_rec_msg.is_connection_close_frame():
                            self.logger.debug("Received Connection Closed")
                            s.close()
                            self.socket_read_list.remove(s)
                            continue
                        else:
                            # Normale Behandlung von Nachrichten, da kein Standardnachricht
                            if ws_rec_msg.is_fin() is not True:
                                # Die Nachricht ist nicht die letzte, also müssen wir diese nun Zwischenspeichern
                                if self.client_sockets[index_of_current_socket]['msg'] is None:
                                    # Das Clientelement hat noch keine Nachricht gespeichert daher speichern wir
                                    # nun die Nachricht für diesen Client zwischen.
                                    self.client_sockets[index_of_current_socket]['msg'] = ws_rec_msg
                                    continue
                                else:
                                    # Wir haben schon Daten zwischengespeichert, also müssen wir die Daten die wir
                                    # nun erhalten haben an die Zwischengespeicherten Daten anhängen
                                    self.client_sockets[index_of_current_socket]['msg'].append_data(ws_rec_msg.data)
                                    continue
                            else:
                                # Wir haben die letzte Nachricht erhalten, wir können die Nachricht nun bearbeiten
                                if self.client_sockets[index_of_current_socket]['msg'] is None:
                                    # Die ganze Nachricht passte in einem Frame, die kann nun behandelt werden.
                                    res = WSRecMessage()
                                    res.set_msg(self.logic_processor.handle(ws_rec_msg))
                                    self.client_sockets[index_of_current_socket]['msg'] = None
                                else:
                                    self.client_sockets[index_of_current_socket]['msg'].append_data(ws_rec_msg.data)
                                    self.client_sockets[index_of_current_socket]['msg'].set_fin()
                                    res = WSRecMessage()
                                    res.set_msg(self.logic_processor.handle(self.client_sockets[index_of_current_socket]['msg']))
                                    self.client_sockets[index_of_current_socket]['msg'] = None
                        if res is not None:
                            s.send(res.get_frame())
                            self.logger.debug("-- " + str(res.get_frame()))
                            continue

                            # Es wurde eine Nachricht ermittelt die nun gesendet werden muss




    def get_response_socket_upgrade(self, decoded_frame):
        """ Creates the response message, if a socket receives the upgrade message """
        response_message = """HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: """
        # Sec-WebSocket-Key: ATfikXxj3s8Pb+vXv5NRLQ==
        decoded_splittet_frame = decoded_frame.split('\r\n')
        sec_websocket_key = ''
        for prop in decoded_splittet_frame:
            if prop.find("Sec-WebSocket-Key") >= 0:
                sec_websocket_key = prop.split(": ")[1]
                if sec_websocket_key.find(" ") >= 0:
                    sec_websocket_key = sec_websocket_key.replace(" ", "")

        print(sec_websocket_key)

        return response_message + self.generate_secure_token(sec_websocket_key) + "\r\n\r\n"

    def generate_secure_token(self, input_key):
        print("Generate secure Key for " + input_key)
        magic_upgrade_key = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        base_key = input_key + magic_upgrade_key
        hash_key = hashlib.sha1(str.encode(base_key, "utf-8")).digest()
        self.logger.debug("Type: " + str(type(hash_key)))
        self.logger.debug("Type: " + str(hash_key))
        encoded_sec_object = base64.b64encode(hash_key)
        return str(encoded_sec_object.decode("utf-8"))

if __name__ == "__main__":
    logger = logging.getLogger("Dev_Log")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(level=logging.DEBUG)
    logger.info("Start Websocket-Server")
    logger.info("Working directory: " + str(os.getcwd()))
    server = WSServer(logger, {'interface' : 'localhost', 'port': 8765, 'mtu': 1500})
    lp = LogicProcessor()
    server.set_logic_processor(lp)
    lp.set_ws_server(server)
    server.start_listen()
    #print("Generated string for dGhlIHNhbXBsZSBub25jZQ==  -> " + server.generate_secure_token('dGhlIHNhbXBsZSBub25jZQ=='))