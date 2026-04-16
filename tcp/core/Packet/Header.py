class Header:
    def __init__(self):
        self._seq_number = 0   # 16 bits
        self._ack_number = 0   # 16 bits
        self._recv_window = 0  # 16 bits
        self._ack_flag = 0     # 1 bit
        self._syn_flag = 0     # 1 bit
        self._fin_flag = 0     # 1 bit
        self._len_data = 0     # 13 bits

    def _check(self, value, bits):
        if value < 0 or value > (2**bits - 1):
            raise ValueError(f"Valor deve caber em {bits} bits")
        return value

    @property
    def seq_number(self):
        return self._seq_number

    @seq_number.setter
    def seq_number(self, value):
        self._seq_number = self._check(value, 16)

    @property
    def ack_number(self):
        return self._ack_number

    @ack_number.setter
    def ack_number(self, value):
        self._ack_number = self._check(value, 16)

    @property
    def recv_window(self):
        return self._recv_window

    @recv_window.setter
    def recv_window(self, value):
        self._recv_window = self._check(value, 16)

    @property
    def ack_flag(self):
        return self._ack_flag

    @ack_flag.setter
    def ack_flag(self, value):
        self._ack_flag = self._check(value, 1)

    @property
    def syn_flag(self):
        return self._syn_flag

    @syn_flag.setter
    def syn_flag(self, value):
        self._syn_flag = self._check(value, 1)

    @property
    def fin_flag(self):
        return self._fin_flag

    @fin_flag.setter
    def fin_flag(self, value):
        self._fin_flag = self._check(value, 1)

    @property
    def len_data(self):
        return self._len_data

    @len_data.setter
    def len_data(self, value):
        self._len_data = self._check(value, 13)

    def to_bytes(self):
        value = (
            (self.seq_number << 48) | # 16 bits
            (self.ack_number << 32) | # 16 bits
            (self.recv_window << 16) | # 16 bits
            (self.len_data << 3) | # 13 bits
            (self.ack_flag << 2) | # 1 bit
            (self.syn_flag << 1) | # 1 bit
            self.fin_flag # 1 bit
        )
        return value.to_bytes(8, "big")
    
    @classmethod
    def from_bytes(cls, data):
        if len(data) != 8:
            raise ValueError("O header deve ter exatamente 8 bytes")

        value = int.from_bytes(data, "big")

        header = cls()

        header.seq_number = (value >> 48) & 0xFFFF   # 16 bits
        header.ack_number = (value >> 32) & 0xFFFF   # 16 bits
        header.recv_window = (value >> 16) & 0xFFFF  # 16 bits
        header.len_data = (value >> 3) & 0x1FFF      # 13 bits
        header.ack_flag = (value >> 2) & 0x1         # 1 bit
        header.syn_flag = (value >> 1) & 0x1         # 1 bit
        header.fin_flag = value & 0x1                # 1 bit

        return header