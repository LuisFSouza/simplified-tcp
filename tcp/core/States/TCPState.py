import logging


class TCPState:
    def __init__(self, context):
        self.context = context

    def transition(self, new_state):
        logging.warning("Transição para estado %s", new_state.__name__)
        self.context.set_state(new_state(self.context))

    def receive(self, packet, addr):
        self.handle_packet(packet, addr)

    def handle_packet(self, packet, addr):
        header = packet.header

        if header.syn_flag == 1 and header.ack_flag == 1:
            return self.on_syn_ack(packet, addr)
        if header.syn_flag == 1:
            return self.on_syn(packet, addr)
        if header.fin_flag == 1:
            return self.on_fin(packet, addr)

        handled = False
        if header.ack_flag == 1:
            self.on_ack(packet, addr)
            handled = True
        if header.len_data > 0:
            self.on_data(packet, addr)
            handled = True
        if not handled:
            self.on_unexpected(packet, addr)

    def on_syn(self, packet, addr):
        self.on_unexpected(packet, addr)

    def on_syn_ack(self, packet, addr):
        self.on_unexpected(packet, addr)

    def on_fin(self, packet, addr):
        self.on_unexpected(packet, addr)

    def on_ack(self, packet, addr):
        self.on_unexpected(packet, addr)

    def on_data(self, packet, addr):
        self.on_unexpected(packet, addr)

    def on_unexpected(self, packet, addr):
        header = packet.header
        logging.warning(
            "Pacote inesperado no estado %s (%s)",
            self.__class__.__name__,
            self._flags_text(header),
        )

    def _flags_text(self, header):
        return (
            f"ack={int(header.ack_flag)} "
            f"syn={int(header.syn_flag)} "
            f"fin={int(header.fin_flag)} "
            f"len={header.len_data}"
        )
