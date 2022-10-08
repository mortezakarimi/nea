import threading


class ThreadHandler(threading.Thread):
    def __init__(self, thread_id, q, cb):
        threading.Thread.__init__(self)
        self.cb = cb
        self.thread_id = str(thread_id)
        self.q = q

    def run(self):
        self.cb(self.q)
