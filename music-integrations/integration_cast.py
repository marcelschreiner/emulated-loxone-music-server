from integration_base import MusicZoneBase
import pychromecast
from pychromecast.controllers.media import MediaStatusListener
from pychromecast.controllers.receiver import CastStatusListener
from pychromecast.controllers.multizone import (
    MultizoneController,
    MultiZoneControllerListener,
)


# Hacky way to get somewhat of a group support for now
group_name = "Gruppe Wohnzimmer"
group_members = ["Wohnzimmer", "Küche", "Erker", "Arbeitszimmer"]


class MusicZoneCast(MusicZoneBase):

    # Share discovered chromecasts across all instances
    chromecasts = None

    def __init__(self, name_of_cast_player):
        super().__init__()

        # Only discover chromecasts if not already done
        if MusicZoneCast.chromecasts is None:
            MusicZoneCast.chromecasts, _ = pychromecast.get_chromecasts()

        for cast_player in MusicZoneCast.chromecasts:
            if cast_player.name == name_of_cast_player:
                self.cast_player = cast_player
                self.cast_player.wait()
                self.cast_player.register_status_listener(self)
                self.cast_player.media_controller.register_status_listener(self)

                # self.mz = MultizoneController(self.cast_player.uuid)
                # self.mz.register_listener(self)
                # self.cast_player.register_handler(self.mz)
                # self.cast_player.register_connection_listener(self)
            elif cast_player.name == group_name and name_of_cast_player in group_members:
                group_player = cast_player
                group_player.wait()
                group_player.register_status_listener(self)
                group_player.media_controller.register_status_listener(self)

    def play(self):
        super().play()
        self.cast_player.media_controller.play()

    def pause(self):
        super().pause()
        self.cast_player.media_controller.pause()

    def stop(self):
        super().stop()
        self.cast_player.media_controller.stop()

    def next(self):
        super().next()
        self.cast_player.media_controller.skip()

    def previous(self):
        super().previous()
        self.cast_player.media_controller.rewind()

    def set_volume(self, volume):
        super().set_volume(volume)
        self.cast_player.set_volume(float(volume) / 100.0)

    def set_time(self, time):
        super().set_time(time * 1000)
        self.cast_player.media_controller.seek(time)

    def set_repeat(self, repeat):
        super().set_repeat(repeat)
        # Repeat mode (0 = none, 1 = track, 2 = context)
        # TODO: Implement repeat for Chromecast

    def set_shuffle(self, shuffle):
        super().set_shuffle(shuffle)
        # Shuffle mode (0 = not shuffled, 1 = shuffled)
        # TODO: Implement shuffle for Chromecast

    def get_name(self):
        return self.cast_player.name

    def get_str(self):
        return super().get_str()

    def _mode_cast_to_loxone(self, mode):
        if mode == "PLAYING":
            return "play"
        elif mode == "PAUSED":
            return "pause"
        elif mode == "UNKNOWN" or mode == "IDLE":
            return "stop"
        elif mode == "BUFFERING":
            return "buffer"
        raise Exception(f'Failed to convert mode from Chromecast to Loxone mode "{mode}" not available')

    def _repeat_cast_to_loxone(self, repeat):
        # TODO: Implement repeat for Chromecast
        return 0

    def new_media_status(self, status):
        print("New media status ", self.cast_player.name)
        artist = status.artist
        title = status.title
        album = status.album_name
        playback_status = status.player_state

        if playback_status:
            self.player.mode = self._mode_cast_to_loxone(status.player_state)
        if status.current_time:
            self.player.set_time(status.current_time * 1000)
        self.player.repeat = 0
        self.player.shuffle = 0

        # if status.session_id:
        #    self.track.id = status.session_id
        if title:
            self.track.title = title
        if album:
            self.track.album = album
        if artist:
            self.track.artist = artist
        if status.duration:
            self.track.duration = status.duration * 1000
        try:
            self.track.image = status.images[0].url
        except IndexError:
            self.track.image = ""  # No image available

    def load_media_failed(self, item, error_code):
        print("Media failed", item, error_code)

    def new_cast_status(self, status):
        print("New cast status ", self.cast_player.name)
        self.player.volume = int(round(status.volume_level * 100))

    def load_cast_failed(self, item, error_code):
        print("Cast failed", item, error_code)

    def multizone_member_added(self, group_uuid: str) -> None:
        print(f"New member: {group_uuid}")

    def multizone_member_removed(self, group_uuid: str) -> None:
        print(f"Removed member: {group_uuid}")

    def multizone_status_received(self) -> None:
        print(f"Members: {self.mz.members}")

    def new_connection_status(self, status) -> None:
        print(f"New connection status")
        if status.status == "CONNECTED":
            self._mz.update_members()
