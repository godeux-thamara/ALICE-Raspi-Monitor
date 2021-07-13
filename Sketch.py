import json
import time
import itertools
from events.events import Event, SensorEvent
import events.actions
from events.actions import Action
from events.timeline import Timeline
from arduinomanager.ArduinosManager import ArduinosManager
from sensors.sensors import *
from media.MediaManager import MediaManager

__all__ = ['Sketch']


class Sketch:
    """docstring for Sketch."""

    def __init__(self, json_file=None):
        self.timeline = Timeline()
        self.actions = {}
        self.events = {}
        self.sensors = {}
        self.arduinos_manager = ArduinosManager()
        self.arduinos_manager.set_callback(self.data_received)
        self.mediamanager = MediaManager()
        if json_file:
            self.load_from_json(json_file)

        events.actions.sketch = self
        self.arduinos_manager.autodiscover()
        time.sleep(2)

    @property
    def sensor_events(self):
        return {name: event for name, event in self.events.items() if isinstance(event, SensorEvent)}

    def load_from_json(self, json_file):
        sketck_json = json.load(open(json_file))

        # Load sensors
        for sensor in sketck_json['sensors']:
            if sensor['type'] == "distance":
                self.sensors[sensor['name']] = DistanceSensor(sensor['name'])
            elif sensor['type'] == "movement":
                self.sensors[sensor['name']] = MovementSensor(sensor['name'])
            elif sensor['type'] == "color":
                self.sensors[sensor['name']] = ColorSensor(sensor['name'])

        # Load sound channels
        for sound_channel in sketck_json['media_channels']:
            self.mediamanager.add_channel(sound_channel['name'])
            for sound_filename in sound_channel['content']:
                self.mediamanager[sound_channel['name']].add_media(sound_filename)

        # Load actions
        for action in sketck_json['actions']:
            self.actions[action['name']] = Action.from_json(action)

        # Load events
        for event in sketck_json['events']:
            self.events[event['name']] = Event()

        # Load sensors events
        for sensor_event in sketck_json['sensor_events']:
            self.events[sensor_event['name']] = SensorEvent(self.sensors[sensor_event['sensor']])
            self.events[sensor_event['name']].set_condition(sensor_event['condition'])

        # Binding actions to events and events to each other
        for event in itertools.chain(sketck_json['events'], sketck_json['sensor_events']):
            for action in event['start_actions']:
                self.events[event['name']].add_action(self.actions[action])
            for action in event['stop_actions']:
                self.events[event['name']].stop_action(self.actions[action])
            for child_event in event['events']:
                self.events[event['name']].add_event(self.events[child_event])
            for sensor_event in event['start_listening']:
                self.events[event['name']].start_listening_events.append(self.events[sensor_event])
            for sensor_event in event['stop_listening']:
                self.events[event['name']].stop_listening_events.append(self.events[sensor_event])

        # And finally, load timeline
        for timeline_element in sketck_json['timeline']:
            if 'events' in timeline_element:
                for event in timeline_element['events']:
                    self.timeline.add_timed_event(timeline_element['time'], self.events[event])
            if 'actions' in timeline_element:
                for action in timeline_element['actions']:
                    self.timeline.add_timed_event(timeline_element['time'], self.actions[action])


    def data_received(self, data):
        data_parsed = data.split(" ")
        if data_parsed[0] == "sensor" and len(data_parsed) > 2:
            self.sensor_data_received(data_parsed[1], data_parsed[2:])

    def sensor_data_received(self, sensor, data):
        self.sensors[sensor].data_received(data)

    def send(self, *args, arduino=None):
        if arduino is None:
            self.arduinos_manager.broadcast(*args)
        else:
            self.arduinos_manager.send_command(arduino, *args)

    def fire_event(self, event_name):
        self.events[event_name].fire()

    def run(self):
        self.timeline.run()
