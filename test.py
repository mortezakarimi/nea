import time

from PyQt6.QtCore import QThreadPool

from Workers.Worker import Worker


def shit(i):
    print("Thread %d start" % i)
    time.sleep(5)
    print("Thread %d complete" % i)


for i in range(1, 10):
    worker = Worker(shit, i)
    QThreadPool.globalInstance().start(worker)

QThreadPool.globalInstance().waitForDone()
