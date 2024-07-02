from PySide6.QtCore import (
    QObject,
    Signal,
    QThread,
    QRunnable,
    QThreadPool,
    SignalInstance,
)


class UID:
    __i = 0

    def get():
        UID.__i += 1
        return UID.__i

    def max():
        return UID.__i


class ThreadWorker(QThread):
    __on_start_callback = Signal(int)
    __on_finish_callback = Signal(int)

    def __init__(
        self,
        thread: QRunnable,
        uid: int,
        finish_callback: object | None = None,
        start_callback: object | None = None,
    ) -> None:
        super().__init__()
        if start_callback != None:
            self.__on_start_callback.connect(start_callback)
        if finish_callback != None:
            self.__on_finish_callback.connect(finish_callback)
        self.__thread = thread
        self.__uid = uid

    def run(self):
        if self.__on_start_callback != None:
            self.__on_start_callback.emit(self.__uid)
        self.__thread.run()
        if self.__on_finish_callback != None:
            self.__on_finish_callback.emit(self.__uid)


class RunnableWrapperSignals(QObject):
    _on_start_callback = Signal(int)
    _on_finish_callback = Signal(int)


class RunnableWrapper(QRunnable):
    def __init__(
        self,
        thread: QRunnable,
        uid: int,
        finish_callback: object | None = None,
        start_callback: object | None = None,
    ) -> None:
        super().__init__()
        self.signals = RunnableWrapperSignals()
        if start_callback != None:
            self.signals._on_start_callback.connect(start_callback)
        if finish_callback != None:
            self.signals._on_finish_callback.connect(finish_callback)
        self.__thread = thread
        self.__uid = uid

    def run(self):
        self.signals._on_start_callback.emit(self.__uid)
        self.__thread.run()
        self.signals._on_finish_callback.emit(self.__uid)


class ThreadManager:
    def __init__(self, maxthreads: int | None = None) -> None:
        self.__MAX_EXECUTED_TASK_TRACKING = 10000

        self.__pool = QThreadPool()
        self.__maxthreads = self.__pool.maxThreadCount()
        if maxthreads != None:
            self.__pool.setMaxThreadCount(maxthreads)
            self.__maxthreads = maxthreads
        self.__threads_pool: dict[str, QRunnable] = {}
        self.__threads_forced: dict[str, QRunnable] = {}
        self.__executed_tasks: list[int] = [0] * self.__MAX_EXECUTED_TASK_TRACKING
        self.__callbacks: dict = {}
        self.__current_tracking_index = 0
        # Tracks the state of a task {uid: (state, forced)} forced: 0 => waiting, 1 => running, 2 => finished

    def __start(self, uid: int) -> None:
        if str(uid) in self.__callbacks:
            self.__callbacks[str(uid)].__call__()

    def __finish(self, uid: int) -> None:
        if str(uid) in self.__threads_pool:
            self.__threads_pool.pop(str(uid))
        else:
            self.__threads_forced.pop(str(uid))

    def runTask(
        self,
        task: QRunnable,
        force: bool = False,
        on_start_callback: object | None = None,
    ) -> int:
        uid = UID.get()

        self.__executed_tasks[self.__current_tracking_index] = uid
        self.__current_tracking_index = (
            self.__current_tracking_index + 1
        ) % self.__MAX_EXECUTED_TASK_TRACKING
        if on_start_callback:
            self.__callbacks[str(uid)] = on_start_callback
        if force:
            worker = ThreadWorker(task, uid, self.__finish, self.__start)
            self.__threads_forced[str(uid)] = worker
            worker.start()
        else:
            worker = RunnableWrapper(task, uid, self.__finish, self.__start)
            self.__threads_pool[str(uid)] = worker
            self.__pool.start(worker)
        return uid

    def getMaxThreadCount(self) -> int:
        return self.__maxthreads

    def setMaxThreadCount(self, count: int) -> None:
        self.__maxthreads = count
        self.__pool.setMaxThreadCount(count)

    def getRunningThreadCount(self, force: bool = False) -> int:
        if force:
            return len(self.__threads_forced)
        return len(self.__threads_pool)

    def queryTaskState(self, uid: int) -> str:
        if str(uid) in self.__threads_forced:
            return f"uid:{uid}/state:running/mode:forced"
        if str(uid) in self.__threads_pool:
            return f"uid:{uid}/state:unknown/mode:pool/assume:{'finished' if self.getRunningThreadCount() <= self.getMaxThreadCount() else 'queued'}"
        if uid in self.__executed_tasks:
            return f"uid:{uid}/state:finished/mode:unknown"
        if uid <= UID.max():
            return f"uid:{uid}/state:unknown/assume:finished+expired"
        return f"uid:{uid}/state:unknown/assume:invalid"


MANAGER = ThreadManager(10)

if __name__ == "__main__":
    import sys, random, time
    from PySide6.QtCore import QCoreApplication

    class randomWaiter(QRunnable):
        def __init__(self, id) -> None:
            super().__init__()
            self.wt = random.randint(1, 10)
            self.id = id
            print(f"{self.id} is created!")

        def run(self):
            print(f"{self.id} is started!")
            time.sleep(self.wt)
            print(f"{self.id} is done!")

    __app__ = QCoreApplication()
    for i in range(100):
        MANAGER.runTask(randomWaiter(i), True)
    MANAGER.getMaxThreadCount()
    sys.exit(__app__.exec())
