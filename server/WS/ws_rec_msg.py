"""
     0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-------+-+-------------+-------------------------------+
    |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
    |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
    |N|V|V|V|       |S|             |   (if payload len==126/127)   |
    | |1|2|3|       |K|             |                               |
    +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
    |     Extended payload length continued, if payload len == 127  |
    + - - - - - - - - - - - - - - - +-------------------------------+
    |                               |Masking-key, if MASK set to 1  |
    +-------------------------------+-------------------------------+
    | Masking-key (continued)       |          Payload Data         |
    +-------------------------------- - - - - - - - - - - - - - - - +
    :                     Payload Data continued ...                :
    + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
    |                     Payload Data continued ...                |
    +---------------------------------------------------------------+
"""

class WSRecMessage():
    """
    Behandelt einen WS_Message, nimmt einen Frame entgegen und splittet diesen in seine Bestandteile auf.
    """

    def msg_to_frame(self):
        """ Generiert den Frame aus den anderen Bestandteilen"""
        return

    def __init__(self):
        self.frame_as_bytes = None
        self.FIN = None
        self.opcode = None
        self.mask = None
        self.payload_len = None
        self.data = None
        self.decoded_data = None
        return

    def set_frame(self, frame_as_bytes):
        self.frame_as_bytes = frame_as_bytes
        return

    def set_msg(self, fin, opcode, decoded_data):
        self.FIN = fin
        self.opcode = opcode
        self.decoded_data = decoded_data
        return


    def frame_to_msg(self):

        if self.frame_as_bytes is None:
            print("Error no Frame set")
            return False
        print("Getting Frame of type: " + str(type(self.frame_as_bytes)))
        print("Number of Bytes: " + str(len(self.frame_as_bytes)))


        self.FIN =          (self.frame_as_bytes[0] & 0b10000000) >> 8
        self.opcode =       (self.frame_as_bytes[0] & 0b00001111)
        self.payload_len =  (self.frame_as_bytes[1] & 0b01111111)

        if self.payload_len < 126:

            self.mask = bytearray()
            for i in range(2, 5+1):
                self.mask.append(self.frame_as_bytes[i])

            self.data = bytearray()
            for i in range(6, len(self.frame_as_bytes)):
                self.data.append(self.frame_as_bytes[i])
            print("Maske: " + str(self.mask.hex()))
        elif self.payload_len == 127:

            print("Wow much content")
            self.extended_len = bytearray()
            self.extended_len.append(self.frame_as_bytes[2])
            self.extended_len.append(self.frame_as_bytes[3])
            self.mask = bytearray()
            for i in range(4, 7+1):
                self.mask.append(self.frame_as_bytes[i])

            self.data = bytearray()
            for i in range(8, len(self.frame_as_bytes)):
                self.data.append(self.frame_as_bytes[i])

            #self.data = frame_as_bytes[6: len(frame_as_bytes)]
        elif self.payload_len == 128:

            print("WOW WOW Much Content")
            self.extended_len = bytearray()
            for i in range(2, 9+1):
                self.extended_len.append(self.frame_as_bytes[i])

            self.mask = bytearray()
            for i in range(10, 13):
                self.mask.append(self.frame_as_bytes[i])

            self.data = bytearray()
            for i in range(14, len(self.frame_as_bytes)):
                self.data.append(self.frame_as_bytes[i])
            #self.data = frame_as_bytes[14: len(frame_as_bytes)]

        # Decodieren des Daten nach RFC6455 (Maskierung)
        self.decoded_data = bytearray()
        print("Datenlänge: " + str(self.payload_len))

        for i in range(0, len(self.data)):
            self.decoded_data.append(self.data[i] ^ self.mask[i % 4])
        print("Decoded data: " + str(self.decoded_data))
        return True

    def is_continuation_frame(self):
        """ Gibt die Information zurück ob das Packet eine fortführung von einem vorherigen Paket ist."""
        if self.opcode == 0:
            return True
        else:
            return False

    def get_msg_as_str(self):
        return str(self.data, "utf-8")

    def add_data(self, data_as_bytes):
        if self.FIN == 0:
            for i in range(0, len(data_as_bytes)):
                self.data.append(data_as_bytes[i])
            return True
        else:
            return False

    def is_fin(self):
        if self.FIN == 0:
            return True
        else:
            return False