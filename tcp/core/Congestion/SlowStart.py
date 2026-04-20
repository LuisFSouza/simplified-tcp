from tcp.core.Congestion.CongestionControlState import CongestionControlState
from tcp.core.Congestion.CongestionAvoidance import CongestionAvoidance

class SlowStart(CongestionControlState):
    def ack_receive(self, machine):
        machine.cwnd += machine.mss

        if machine.cwnd >= machine.ssthresh:
            machine.state = CongestionAvoidance()

    def timeout(self, machine):
        machine.ssthresh = max(machine.cwnd / 2, machine.mss)
        machine.cwnd = machine.mss
        machine.state = SlowStart()