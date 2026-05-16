from tcp.core.Congestion.SlowStart import SlowStart

class CongestionControl:
    def __init__(self, mss=1024, ssthresh=15360):
        self.mss = mss
        self.cwnd = mss
        self.ssthresh = ssthresh
        self.state = SlowStart()

    def ack_receive(self):
        self.state.ack_receive(self)

    def timeout(self):
        self.state.timeout(self)
        
    def three_dup_ack(self):
        self.state.three_dup_ack(self)

    def additional_dup_ack(self):
        self.state.additional_dup_ack(self)

    def get_cwnd(self):
        return self.cwnd
    
    def get_ssthresh(self):
        return self.ssthresh