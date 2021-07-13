import threading

__all__ = ['Timeline']


class Timeline:
    """docstring for Timeline."""

    def __init__(self):
        self.events_timers = []

    def add_timed_event(self, time: float, event, *args, **kwargs):
        self.events_timers.append(threading.Timer(time, event, args=args, kwargs=kwargs))

    def run(self):
        for timer in self.events_timers:
            timer.start()
