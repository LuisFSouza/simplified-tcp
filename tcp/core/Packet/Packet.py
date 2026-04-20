from tcp.core.Packet.Header import Header

class Packet:
    def __init__(self, payload=b"", seq_number=0, ack_number=0, ack_flag=0, syn_flag=0, fin_flag=0):
        self._header = Header(seq_number, ack_number, len(self._payload), 0, ack_flag, syn_flag, fin_flag)
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
        if len(data) < Header.SIZE:
            raise ValueError(f"Pacote inválido: menor que {Header.SIZE} bytes")

        header_bytes = data[:Header.SIZE]
        payload = data[Header.SIZE:]

        packet = cls(payload=payload)
        packet.header = Header.from_bytes(header_bytes)

        return packet