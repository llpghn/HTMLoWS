from server.WS.ws_rec_msg import WSRecMessage

class LogicProcessor:
    """
    LogicProcessor, welche die Datenbank und auch die Templates verwaltet.
        * Bearbeitet Nachrichten auf logische Ebene
        * Baut Antworten zusammen / Generiert HTML
        * Verwaltet VDOMs
        * Interpretiert Payload
    """

    def __init__(self):
        print("Starte LogicProcessor")

    def handle(self, message, client):
        """ Wir haben eine Nachricht die Verarbeitet werden muss, diese Nachricht enthält nun sicher
            einen Payload und wird von einem entsprechenden Client ausgelöst. Wir müssen nun die Nachricht
            die als String vorliegt analysieren und dann entsprechende Gegenaktionen durchführen. """

        return '<!--Main--><div id="Message">Dummy return!</div>'

    def set_ws_server(self):
        """

        """