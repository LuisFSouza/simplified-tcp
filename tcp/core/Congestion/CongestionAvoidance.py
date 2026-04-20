from tcp.core.Congestion.CongestionControlState import CongestionControlState
from tcp.core.Congestion.SlowStart import SlowStart

class CongestionAvoidance(CongestionControlState):
    def ack_receive(self, machine):
        machine.cwnd += (machine.mss * machine.mss) / machine.cwnd

    def timeout(self, machine):
        machine.ssthresh = max(machine.cwnd / 2, machine.mss)
        machine.cwnd = machine.mss
        machine.state = SlowStart()