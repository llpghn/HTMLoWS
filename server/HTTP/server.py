import socket
import logging # Logging
import os


class HTTPServer():
    """
    Webserver Komponente, die rein die Clientanwendung auf HTTP-Get anfragen ausliefert.
    """
    def __init__(self, logger, configuration):
        self.logger = logger
        self.configuration = configuration
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((configuration['interface'], configuration['port']))
        self.socket.listen(5)

    def start_listen(self):
        while True:
            # Establish connection with client.
            client, addr = self.socket.accept()
            print('Got connection from', addr)

            # send a thank you message to the client.
            #client.send('Thank you for connecting')
            self.logger.debug("Conn-Info: " + str(addr))
            rec_data = client.recv(self.configuration['mtu'])

            #self.get_response_msg(rec_data.decode("utf-8"))

            client.send(self.get_response_msg(rec_data.decode("utf-8")))

            self.logger.debug(rec_data.decode("utf-8") )
            # Close the connection with the client
            client.close()

    def get_closing_msg(self):
        response = """HTTP/1.1 200 Ok\r\nConnection: close\r\n\r\n"""
        return bytes(response, 'utf-8')
    def get_response_msg(self, decoded_msg):
        response = ''
        if decoded_msg.find(' / ') != -1 and decoded_msg.find('Connection: keep-alive') != -1:
            # Client sends Request for
            client_file = open("./client/index.html", "r")
            html_response = client_file.read()
            # /client wurde im Request gefunden, also liefern wir nun die Startseite aus.
            response = """HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n""" + html_response
            return bytes(response, 'utf-8')
        else:
            # /cliet nicht gefunden
            response = """HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nBAD REQUEST
            """
            return bytes(response, 'utf-8')


if __name__ == "__main__":
    logger = logging.getLogger("Dev_Log")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(level=logging.DEBUG)
    logger.info("Start HOW-Server")
    logger.info("Working directory: " + str(os.getcwd()))
    server = HTTPServer(logger, {'interface' : 'localhost', 'port': 8000, 'mtu': 1500})
    server.start_listen()