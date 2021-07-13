import threading
import vlc
from media.MediaPlayer import MediaPlayer

__all__ = ['MediaManager']


class MediaManager:
    """docstring for MediaManager."""

    def __init__(self):
        self.players = {}

    def add_channel(self, name: str):
        if name in self.players.keys():
            raise ValueError("A channel already exists with that name")
        self.players[name] = MediaPlayer()

    def play(self, channel: str):
        self.players[channel].play()

    def pause(self, channel: str):
        self.players[channel].pause()

    def stop(self, channel: str):
        self.players[channel].stop()

    def play_all(self):
        [channel.play() for channel in self.players.values()]

    def pause_all(self):
        [channel.pause() for channel in self.players.values()]

    def stop_all(self):
        [channel.stop() for channel in self.players.values()]

    def play_now(self, sound_filename, volume: int = 100, other_channels_volume: int = None, fade_time: float = 0):
        player = MediaPlayer()
        player.volume = volume
        media = vlc.Media(sound_filename)
        media.parse()
        duration = media.get_duration() / 1000
        player.add_media(media)
        if other_channels_volume is not None:
            self.fade_all_channels(other_channels_volume, fade_time, duration)
        player.play()

    def set_volume(self, channel: str, volume: int, fade_time: float = 0):
        self.players[channel].fade(fade_time, volume)

    def set_all_volumes(self, volume: int = 100, fade_time: float = 0):
        for channel in self.players:
            self.set_volume(channel, volume, fade_time)

    reset_all_volumes = set_all_volumes

    def fade_channel(self, channel: str, volume: int, fade_time: float, duration: float):
        previous_volume = self[channel].volume
        self.set_volume(channel, volume, fade_time)
        threading.Timer(duration, self.set_volume, args=(channel, previous_volume, fade_time)).start()

    def fade_channels(self, channels: list, *args, **kwargs):
        for channel in channels:
            self.fade_channel(channel, *args, **kwargs)

    def fade_all_channels(self, *args, **kwargs):
        self.fade_channels(self.players.keys(), *args, **kwargs)

    def foreground_channel(self, channel: str, low_volume: int = 60, high_volume: int = 100, fade_time: float = 0, duration: float = None):
        for channel_name, player in self.players.items():
            if channel_name == channel:
                player.fade(fade_time, high_volume)
            else:
                player.fade(fade_time, low_volume)
        if duration:
            threading.Timer(duration, self.set_all_volumes, kwargs={"fade_time":fade_time}).start()

    def __getitem__(self, item):
        return self.players[item]
