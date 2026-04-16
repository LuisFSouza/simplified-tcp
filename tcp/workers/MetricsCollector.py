import logging
import time
import matplotlib.pyplot as plt


class MetricsCollector:
    def __init__(self):
        self.window = {
            "timestamps": [],
            "cwnd": [],
            "ssthresh": [],
            "bytes_in_flight": [],
            "send_queue_size": [],
        }
        self.ack = {"timestamps": [], "acked_bytes": []}
        self.received = {"timestamps": [], "received_bytes": []}
        self.retransmit = {"timestamps": [], "retransmissions": []}
        self.rtt = {"timestamps": [], "rtt_ms": []}
        self._acked_total = 0
        self._received_total = 0
        self._retransmit_total = 0

    def record_window(self, cwnd, ssthresh, bytes_in_flight, send_queue_size):
        ts = time.time()
        self.window["timestamps"].append(ts)
        self.window["cwnd"].append(cwnd)
        self.window["ssthresh"].append(ssthresh)
        self.window["bytes_in_flight"].append(bytes_in_flight)
        self.window["send_queue_size"].append(send_queue_size)

    def record_acked(self, acked_bytes):
        if acked_bytes <= 0:
            return
        self._acked_total += acked_bytes
        self.ack["timestamps"].append(time.time())
        self.ack["acked_bytes"].append(self._acked_total)

    def record_received(self, received_bytes):
        if received_bytes <= 0:
            return
        self._received_total += received_bytes
        self.received["timestamps"].append(time.time())
        self.received["received_bytes"].append(self._received_total)

    def record_retransmit(self):
        self._retransmit_total += 1
        self.retransmit["timestamps"].append(time.time())
        self.retransmit["retransmissions"].append(self._retransmit_total)

    def record_rtt(self, rtt_seconds):
        if rtt_seconds < 0:
            return
        self.rtt["timestamps"].append(time.time())
        self.rtt["rtt_ms"].append(rtt_seconds * 1000)

    def plot(self, output_path="metrics.png", show=True):
        starts = []
        for series in (self.window, self.ack, self.received, self.retransmit, self.rtt):
            if series["timestamps"]:
                starts.append(series["timestamps"][0])
        if not starts:
            logging.warning("Nenhuma metrica coletada para plotar.")
            return

        start = min(starts)

        fig, axes = plt.subplots(2, 3, figsize=(16, 8))

        self._plot_window_metrics(axes[0, 0], start)
        self._plot_bytes_in_flight(axes[0, 1], start)
        self._plot_rtt(axes[0, 2], start)
        self._plot_throughput(axes[1, 0], start)
        self._plot_cumulative_events(axes[1, 1], start)
        self._plot_retransmissions(axes[1, 2], start)

        plt.tight_layout()
        plt.savefig(output_path)
        if show:
            plt.show()

    def _relative_time(self, timestamps, start):
        return [ts - start for ts in timestamps]

    def _plot_window_metrics(self, axis, start):
        plotted = False
        if self.window["timestamps"]:
            ts = self._relative_time(self.window["timestamps"], start)
            axis.plot(ts, self.window["cwnd"], label="cwnd")
            axis.plot(ts, self.window["ssthresh"], label="ssthresh")
            plotted = True
        axis.set_title("Congestion window")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Bytes")
        if plotted:
            axis.legend()

    def _plot_bytes_in_flight(self, axis, start):
        plotted = False
        if self.window["timestamps"]:
            ts = self._relative_time(self.window["timestamps"], start)
            axis.plot(ts, self.window["bytes_in_flight"], label="bytes in flight")
            plotted = True
        axis.set_title("Bytes in flight")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Bytes")
        if plotted:
            axis.legend()

    def _plot_rtt(self, axis, start):
        plotted = False
        if self.rtt["timestamps"]:
            ts = self._relative_time(self.rtt["timestamps"], start)
            axis.plot(ts, self.rtt["rtt_ms"], label="rtt")
            plotted = True
        axis.set_title("RTT")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("ms")
        if plotted:
            axis.legend()

    def _plot_throughput(self, axis, start):
        plotted = False
        if len(self.ack["timestamps"]) >= 2:
            ts = []
            throughput = []
            times = self.ack["timestamps"]
            bytes_list = self.ack["acked_bytes"]
            for i in range(1, len(times)):
                dt = times[i] - times[i - 1]
                if dt <= 0:
                    continue
                ts.append(times[i])
                throughput.append((bytes_list[i] - bytes_list[i - 1]) / dt)
            if ts:
                ts_rel = self._relative_time(ts, start)
                axis.plot(ts_rel, throughput, label="throughput")
                plotted = True
        axis.set_title("Throughput")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Bytes/s")
        if plotted:
            axis.legend()

    def _plot_cumulative_events(self, axis, start):
        plotted = False
        if self.ack["timestamps"]:
            ts = self._relative_time(self.ack["timestamps"], start)
            axis.plot(ts, self.ack["acked_bytes"], label="acked bytes")
            plotted = True
        if self.received["timestamps"]:
            ts = self._relative_time(self.received["timestamps"], start)
            axis.plot(ts, self.received["received_bytes"], label="received bytes")
            plotted = True
        axis.set_title("Cumulative events")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Count / Bytes")
        if plotted:
            axis.legend()

    def _plot_retransmissions(self, axis, start):
        plotted = False
        if self.retransmit["timestamps"]:
            ts = self._relative_time(self.retransmit["timestamps"], start)
            axis.step(ts, self.retransmit["retransmissions"], where="post", label="retransmissions")
            axis.scatter(ts, self.retransmit["retransmissions"], s=16)
            plotted = True
        axis.set_title("Retransmissions")
        axis.set_xlabel("Time (s)")
        axis.set_ylabel("Count")
        if plotted:
            axis.legend()
