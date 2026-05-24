import logging
from tcp.core.Congestion.CongestionControlState import CongestionControlState

class CongestionAvoidance(CongestionControlState):
    def ack_receive(self, machine):
        old_cwnd = machine.cwnd
        machine.cwnd += (machine.mss * machine.mss) // machine.cwnd
        logging.warning(f"[CongestionAvoidance] ACK recebido: cwnd {old_cwnd:.2f} -> {machine.cwnd:.2f}")

    def timeout(self, machine):
        from tcp.core.Congestion.SlowStart import SlowStart
        old_cwnd = machine.cwnd
        old_ssthresh = machine.ssthresh
        machine.ssthresh = max(machine.cwnd // 2, machine.mss)
        machine.cwnd = machine.mss
        logging.warning(f"[CongestionAvoidance -> SlowStart] Timeout: cwnd {old_cwnd} -> {machine.cwnd}, ssthresh {old_ssthresh} -> {machine.ssthresh}")
        machine.state = SlowStart()
        
    def three_dup_ack(self, machine):
        from tcp.core.Congestion.FastRecovery import FastRecovery
        old_cwnd = machine.cwnd
        old_ssthresh = machine.ssthresh
        machine.ssthresh = max(machine.cwnd // 2, machine.mss)
        machine.cwnd = machine.ssthresh + 3 * machine.mss
        logging.warning(f"[CongestionAvoidance -> FastRecovery] 3 ACKs duplicados: cwnd {old_cwnd} -> {machine.cwnd}, ssthresh {old_ssthresh} -> {machine.ssthresh}")
        machine.state = FastRecovery()