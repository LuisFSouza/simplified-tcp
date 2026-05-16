from tcp.core.Congestion.CongestionControlState import CongestionControlState

class CongestionAvoidance(CongestionControlState):
    def ack_receive(self, machine):
        machine.cwnd += (machine.mss * machine.mss) / machine.cwnd

    def timeout(self, machine):
        from tcp.core.Congestion.SlowStart import SlowStart
        machine.ssthresh = max(machine.cwnd / 2, machine.mss)
        machine.cwnd = machine.mss
        machine.state = SlowStart()
        
    def three_dup_ack(self, machine):
        from tcp.core.Congestion.FastRecovery import FastRecovery
        machine.ssthresh = max(machine.cwnd / 2, machine.mss)
        machine.cwnd = machine.ssthresh + 3 * machine.mss
        machine.state = FastRecovery()