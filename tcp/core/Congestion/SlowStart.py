
import logging
from tcp.core.Congestion.CongestionControlState import CongestionControlState

class SlowStart(CongestionControlState):
    def ack_receive(self, machine):
        from tcp.core.Congestion.CongestionAvoidance import CongestionAvoidance
        old_cwnd = machine.cwnd
        machine.cwnd += machine.mss
        logging.warning(f"[SlowStart] ACK recebido: cwnd {old_cwnd} -> {machine.cwnd}")

        if machine.cwnd >= machine.ssthresh:
            logging.warning(f"[SlowStart -> CongestionAvoidance] cwnd ({machine.cwnd}) >= ssthresh ({machine.ssthresh})")
            machine.state = CongestionAvoidance()

    def timeout(self, machine):
        old_cwnd = machine.cwnd
        old_ssthresh = machine.ssthresh
        machine.ssthresh = max(machine.cwnd // 2, machine.mss)
        machine.cwnd = machine.mss
        logging.warning(f"[SlowStart] Timeout: cwnd {old_cwnd} -> {machine.cwnd}, ssthresh {old_ssthresh} -> {machine.ssthresh}")
        machine.state = SlowStart()
        
    def three_dup_ack(self, machine):
        from tcp.core.Congestion.FastRecovery import FastRecovery
        old_cwnd = machine.cwnd
        old_ssthresh = machine.ssthresh
        machine.ssthresh = max(machine.cwnd // 2, machine.mss)
        machine.cwnd = machine.ssthresh + 3 * machine.mss
        logging.warning(f"[SlowStart -> FastRecovery] 3 ACKs duplicados: cwnd {old_cwnd} -> {machine.cwnd}, ssthresh {old_ssthresh} -> {machine.ssthresh}")
        machine.state = FastRecovery()