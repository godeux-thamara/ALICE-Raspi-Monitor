"""
pydub
pyglet

pygame
pymedia
"""

import threading
import time
import vlc

__all__ = ['MediaPlayer']


class MediaPlayer:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, autofade: bool = False, fading_time: float = 0):
        super().__init__()
        self._medialist = vlc.MediaList()
        self._medialistplayer = vlc.MediaListPlayer()
        self._medialistplayer.set_media_list(self._medialist)
        self._player = self._medialistplayer.get_media_player()

        # Setting default volume level to 100
        self.volume = self._old_volume = 100
        # Fading time, in seconds
        self.fading_time = fading_time
        # Auto fading between songs
        self.autofade = autofade
        self._autofade_thread = None

    @property
    def volume(self) -> int:
        return self._player.audio_get_volume()

    @volume.setter
    def volume(self, volume: int):
        self.set_volume(volume)

    def set_volume(self, volume: int) -> bool:
        return not self._player.audio_set_volume(volume)

    def toggle_mute(self):
        self._player.audio_toggle_mute()

    def mute(self):
        self._player.audio_set_mute(True)

    def unmute(self):
        self._player.audio_set_mute(False)

    def add_media(self, filename: str):
        self._medialist.add_media(filename)

    @property
    def queue_length(self) -> int:
        return self._medialist.count()

    def __len__(self):
        return self.queue_length()

    def reset_playlist(self):
        self._medialist = vlc.MediaList()
        self._medialistplayer.set_media_list(self._medialist)

    def play(self):
        self._medialistplayer.play()

    def stop(self):
        self._medialistplayer.stop()

    def pause(self):
        self._medialistplayer.pause()

    def next(self):
        self._medialistplayer.next()

    def previous(self):
        self._medialistplayer.previous()

    def play_item_at_index(self, index):
        self._medialistplayer.play_item_at_index(index)

    def is_playing(self) -> bool:
        return bool(self._player.is_playing())

    def set_loop(self, loopmode: str):
        if loopmode == "loop":
            self._medialistplayer.set_playback_mode(vlc.PlaybackMode.loop)
        elif loopmode == "repeat":
            self._medialistplayer.set_playback_mode(vlc.PlaybackMode.repeat)
        else:
            self._medialistplayer.set_playback_mode(vlc.PlaybackMode.default)

    def _fade(self, fading_time: float, volume: int, verbose: bool = False):
        if self.volume == volume:
            return
        if fading_time == 0:
            self.volume = volume
            return
        volume_diff = volume - self.volume
        while self.volume != volume:
            self.volume += (1 if volume_diff > 0 else -1)
            if verbose: print(f"Volume = {self.volume}")
            time.sleep(abs(fading_time / volume_diff))
        if verbose: print(f"Volume = {self.volume}")

    def fade(self, *args, **kwargs):
        threading.Thread(target=self._fade, args=args, kwargs=kwargs).start()

    def _fade_and_pause(self, fading_time: float):
        self._fade(fading_time, 0)
        self.pause()

    def fade_and_pause(self, *args, **kwargs):
        threading.Thread(target=self._fade_and_pause, args=args, kwargs=kwargs).start()

    def _fade_and_play(self, fading_time: float):
        # p.volume = 0
        self.play()
        self._fade(fading_time, 100)

    def fade_and_play(self, *args, **kwargs):
        threading.Thread(target=self._fade_and_play, args=args, kwargs=kwargs).start()

    @property
    def autofade(self) -> bool:
        return self._autofadeEnabled

    @autofade.setter
    def autofade(self, value: bool):
        if value:
            self._autofadeEnabled = True
            self.start_autofade()
        else:
            self._autofadeEnabled = False

    def _autofade(self):
        while self.autofade:
            if self._player.get_length() != -1 and self._player.get_time() != -1 and self.is_playing():
                if (self._player.get_length() - self._player.get_time()) / 1000 < self.fading_time:
                    self._old_volume = self.volume
                    self._fade(self.fading_time, 0)
                elif self._player.get_time() / 1000 < self.fading_time:
                    self.volume = 0
                    self._fade(self.fading_time, self._old_volume)

    def start_autofade(self):
        self._autofade_thread = threading.Thread(target=self._autofade)
        self._autofade_thread.start()

    def _play_media(self, media_index, transition_time: float = 0):
        old_volume = self.volume
        self._fade(transition_time, 0)
        self.play_item_at_index(media_index)
        self._fade(transition_time, 0)
        self._fade(transition_time, old_volume)

    def play_media(self, *args, **kwargs):
        threading.Thread(target=self._play_media, args=args, kwargs=kwargs).start()

    def __del__(self):
        self.autofade = False

    def __getitem__(self, item):
        return self._medialist.item_at_index(item)
