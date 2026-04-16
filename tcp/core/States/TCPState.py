import logging


class PacketEvent:
    def __init__(self, header):
        self.seq_number = header.seq_number
        self.ack_number = header.ack_number
        self.ack_flag = header.ack_flag == 1
        self.syn_flag = header.syn_flag == 1
        self.fin_flag = header.fin_flag == 1
        self.data_len = header.len_data

    def flags_text(self):
        return (
            f"ack={int(self.ack_flag)} "
            f"syn={int(self.syn_flag)} "
            f"fin={int(self.fin_flag)} "
            f"len={self.data_len}"
        )


class TCPState:
    def __init__(self, context):
        self.context = context

    def transition(self, new_state_cls):
        self.context.set_state(new_state_cls(self.context))

    def receive(self, packet, addr):
        self.handle_packet(packet, addr)

    def handle_packet(self, packet, addr):
        header = packet.header
        event = PacketEvent(header)

        if event.syn_flag and event.ack_flag:
            return self.on_syn_ack(packet, addr, event)
        if event.syn_flag:
            return self.on_syn(packet, addr, event)
        if event.fin_flag:
            return self.on_fin(packet, addr, event)

        handled = False
        if event.ack_flag:
            self.on_ack(packet, addr, event)
            handled = True
        if event.data_len > 0:
            self.on_data(packet, addr, event)
            handled = True
        if not handled:
            self.on_unexpected(packet, addr, event)

    def on_syn(self, packet, addr, event):
        self.on_unexpected(packet, addr, event)

    def on_syn_ack(self, packet, addr, event):
        self.on_unexpected(packet, addr, event)

    def on_fin(self, packet, addr, event):
        self.on_unexpected(packet, addr, event)

    def on_ack(self, packet, addr, event):
        self.on_unexpected(packet, addr, event)

    def on_data(self, packet, addr, event):
        self.on_unexpected(packet, addr, event)

    def on_unexpected(self, packet, addr, event):
        logging.warning(
            "Pacote inesperado no estado %s (%s)",
            self.__class__.__name__,
            event.flags_text(),
        )

