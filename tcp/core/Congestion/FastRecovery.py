from tcp.core.Congestion.CongestionControlState import CongestionControlState

class FastRecovery(CongestionControlState):
    def ack_receive(self, machine):
        from tcp.core.Congestion.CongestionAvoidance import CongestionAvoidance
        machine.cwnd = machine.ssthresh
        machine.state = CongestionAvoidance()
        
    def additional_dup_ack(self, machine):
        machine.cwnd += machine.mss

    def timeout(self, machine):
        from tcp.core.Congestion.SlowStart import SlowStart
        machine.ssthresh = max(machine.cwnd / 2, machine.mss)
        machine.cwnd = machine.mss
        machine.state = SlowStart()