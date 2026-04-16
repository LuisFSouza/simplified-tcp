from tcp.core.Packet.Header import Header

class Packet:
    HEADER_SIZE = 8

    def __init__(self, payload=b""):
        self._header = Header()
        self._payload = bytes(payload)

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        if not isinstance(value, Header):
            raise TypeError("header deve ser uma instancia de Header")
        self._header = value

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        self._payload = bytes(value)

    def to_bytes(self):
        return self.header.to_bytes() + self.payload

    @classmethod
    def from_bytes(cls, data):
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Pacote inválido: menor que o header")

        header_bytes = data[:cls.HEADER_SIZE]
        payload = data[cls.HEADER_SIZE:]

        packet = cls(payload=payload)
        packet.header = Header.from_bytes(header_bytes)
        
        return packet