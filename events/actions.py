from pydispatch import Dispatcher, ListProperty

__all__ = ['Action', 'ArduinoAction', 'SoundAction', 'sketch']

sketch = None


class Action(Dispatcher):
    """base class for all actions"""

    @staticmethod
    def from_json(action_json):
        if action_json['type'] == "sound_action":
            return SoundAction(action_json=action_json)
        if action_json['type'] == 'arduino_action':
            return ArduinoAction(action_json=action_json)
        raise ValueError(f"Unknown action type {action_json['type']}")

    def fire(self):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.fire(*args, **kwargs)

class ArduinoAction(Action):
    """base class for all actions that involve an Arduino (ex: LED, motors...)"""

    parameters = ListProperty()

    #def __init__(self, action, *parameters, arduino_target="ALL", action_json=None):
    def __init__(self, *parameters, action='', arduino_target=None, action_json=None):
        super().__init__()
        self.action = action
        self.parameters = [*parameters]
        self.arduino_target = arduino_target

        if action_json:
            # TODO: complete loading arduino action from json
            self.action = action_json['options']['animation']
            self.parameters = [action_json['options']['parameters']] if 'parameters' in action_json['options'] else []
            self.arduino_target = action_json['options']['arduino'] if 'arduino' in action_json['options'] else None

    def fire(self):
        sketch.send(self.action, *self.parameters, arduino=self.arduino_target)

    def update_params(self):
        sketch.send(self.action + "_params", *self.parameters, arduino=self.arduino_target)

    def stop(self):
        sketch.send(self.action + "_stop", arduino=self.arduino_target)


class SoundAction(Action):
    """Class for any sound action (play/pause a channel, play a sound...)"""

    def __init__(self, action_json):
        super().__init__()
        self.action_json = action_json
        self.parameters = action_json['options']

    def fire(self):
        # play_channel
        if self.action_json['action'] == 'play_channel':
            if 'fade_time' in self.parameters:
                sketch.mediamanager[self.parameters['channel']].fade_and_play(self.parameters['fade_time'])
            else:
                sketch.mediamanager.play(self.parameters['channel'])

        # pause_channel
        elif self.action_json['action'] == 'pause_channel':
            if 'fade_time' in self.parameters:
                sketch.mediamanager[self.parameters['channel']].fade_and_pause(self.parameters['fade_time'])
            else:
                sketch.mediamanager.pause(self.parameters['channel'])

        # set_volume
        elif self.action_json['action'] == 'set_volume':
            sketch.mediamanager.set_volume(
                self.parameters['channel'],
                self.parameters['volume'],
                self.parameters['fade_time'] if 'fade_time' in self.parameters else 0
            )

        # set_loop_mode
        elif self.action_json['action'] == 'set_loop_mode':
            sketch.mediamanager[self.parameters['channel']].set_loop(self.parameters['loop_mode'])

        # play_media_on_channel
        elif self.action_json['action'] == 'play_media_on_channel':
            sketch.mediamanager[self.parameters['channel']].play_media(
                self.parameters['media_index'],
                self.parameters['transition_time'] if 'transition_time' in self.parameters else 0
            )

        # play_sound
        elif self.action_json['action'] == 'play_sound':
            volume = self.parameters['volume'] if 'volume' in self.parameters else 100
            other_volume = self.parameters['other_volume'] if 'other_volume' in self.parameters else 50
            fade_time = self.parameters['fade_time'] if 'fade_time' in self.parameters else 0
            if 'fade_others' in self.parameters and self.parameters['fade_others']:
                sketch.mediamanager.play_now(
                    sound_filename=self.parameters['filename'],
                    volume=volume,
                    other_channels_volume=other_volume,
                    fade_time=fade_time
                )
            else:
                sketch.mediamanager.play_now(
                    sound_filename=self.parameters['filename'],
                    volume=volume,
                )
