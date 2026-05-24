import logging
from tcp.core.Congestion.CongestionControlState import CongestionControlState

class FastRecovery(CongestionControlState):
    def ack_receive(self, machine):
        from tcp.core.Congestion.CongestionAvoidance import CongestionAvoidance
        old_cwnd = machine.cwnd
        machine.cwnd = machine.ssthresh
        logging.warning(f"[FastRecovery -> CongestionAvoidance] ACK do pacote retransmitido: cwnd {old_cwnd} -> {machine.cwnd}")
        machine.state = CongestionAvoidance()
        
    def additional_dup_ack(self, machine):
        old_cwnd = machine.cwnd
        machine.cwnd += machine.mss
        logging.warning(f"[FastRecovery] ACK duplicado adicional: cwnd {old_cwnd} -> {machine.cwnd}")

    def timeout(self, machine):
        from tcp.core.Congestion.SlowStart import SlowStart
        old_cwnd = machine.cwnd
        old_ssthresh = machine.ssthresh
        machine.ssthresh = max(machine.cwnd // 2, machine.mss)
        machine.cwnd = machine.mss
        logging.warning(f"[FastRecovery -> SlowStart] Timeout: cwnd {old_cwnd} -> {machine.cwnd}, ssthresh {old_ssthresh} -> {machine.ssthresh}")
        machine.state = SlowStart()