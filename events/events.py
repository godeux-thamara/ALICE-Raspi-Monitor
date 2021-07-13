from pydispatch import Dispatcher
from sensors.sensors import DistanceSensor, MovementSensor, ColorSensor

__all__ = ['Event', 'SensorEvent']


class Event(Dispatcher):
    """docstring for Event."""

    def __init__(self):
        super().__init__()
        self.start_actions = []
        self.stop_actions = []
        self.events = []
        self.start_listening_events = []
        self.stop_listening_events = []

    def add_action(self, action):
        self.start_actions.append(action)

    def stop_action(self, action):
        self.stop_actions.append(action)

    def add_event(self, event):
        self.events.append(event)

    def fire(self, *args, **kwargs):
        [action.fire(*args, **kwargs) for action in self.start_actions]
        [action.stop(*args, **kwargs) for action in self.stop_actions]
        [event(*args, **kwargs) for event in self.events]
        [event.start_listening() for event in self.start_listening_events]
        [event.stop_listening() for event in self.stop_listening_events]

    emit = fire

    def __call__(self, *args, **kwargs):
        return self.fire(*args, **kwargs)


class SensorEvent(Event):
    """Class for sensor based event"""

    def __init__(self, sensor, condition="0"):
        super().__init__()
        self.sensor = sensor
        self.condition = condition

    def new_data_received(self, _instance, new_data, old_data, _property):
        if self.eval_condition(new_data, old_data):
            self.fire()

    def eval_condition(self, new_data, old_data):
        # TODO: sensor condition evaluation
        variables = {}
        if isinstance(self.sensor, DistanceSensor):
            variables = {"distance": self.sensor.distance}
        elif isinstance(self.sensor, MovementSensor):
            variables = {"movement": self.sensor.movement}
        elif isinstance(self.sensor, ColorSensor):
            variables = {"red": self.sensor.red, "green": self.sensor.green, "blue": self.sensor.blue}

        if eval(self.condition, variables):
            self.stop_listening()
            return True
        return False

    def set_condition(self, cond):
        self.condition = cond

    def start_listening(self):
        self.sensor.bind(values=self.new_data_received)

    def stop_listening(self):
        self.sensor.unbind(self)
