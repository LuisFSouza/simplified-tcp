class ConnectionLifecycle:
    def __init__(self, context, receive_worker, send_worker, retransmit_controller):
        self.context = context
        self.receive_worker = receive_worker
        self.send_worker = send_worker
        self.retransmit_controller = retransmit_controller

    def start(self):
        self.receive_worker.start()
        self.send_worker.start()
        self.retransmit_controller.start()

    def stop(self, join_timeout=1.0):
        self.context.stop_threads = True
        for thread in (
            self.receive_worker.thread,
            self.send_worker.thread,
            self.retransmit_controller.thread,
        ):
            thread.join(timeout=join_timeout)
