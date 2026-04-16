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

    def get_cwnd(self):
        return self.cwnd
