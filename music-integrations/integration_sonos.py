import soco
from soco import snapshot
from integration_base import MusicZoneBase
from datetime import timedelta
import asyncio
from time import sleep


class MusicZoneSonos(MusicZoneBase):
    def __init__(self, name_of_sonos_player):
        super().__init__()
        self.sonos_player = soco.discovery.by_name(name_of_sonos_player)
        loop = asyncio.get_event_loop()
        loop.create_task(self.__update_info())

    def play(self):
        super().play()
        self.sonos_player.group.coordinator.play()

    def pause(self):
        super().pause()
        self.sonos_player.group.coordinator.pause()

    def stop(self):
        super().stop()
        self.sonos_player.group.coordinator.stop()

    def next(self):
        super().next()
        self.sonos_player.group.coordinator.next()

    def previous(self):
        super().previous()
        self.sonos_player.group.coordinator.previous()

    def set_volume(self, volume):
        super().set_volume(volume)
        self.sonos_player.volume = volume

    def set_time(self, time):
        super().set_time(time * 1000)
        self.sonos_player.group.coordinator.seek(str(timedelta(seconds=time)))

    def set_repeat(self, repeat):
        super().set_repeat(repeat)
        # Repeat mode (0 = none, 1 = track, 2 = context)
        if repeat == 0:
            self.sonos_player.group.coordinator.repeat = False
        elif repeat == 1:
            self.sonos_player.group.coordinator.repeat = "ONE"
        elif repeat == 2:
            self.sonos_player.group.coordinator.repeat = True

    def set_shuffle(self, shuffle):
        super().set_shuffle(shuffle)
        # Shuffle mode (0 = not shuffled, 1 = shuffled)
        self.sonos_player.group.coordinator.shuffle = bool(shuffle)

    def set_sync(self, name_of_sonos_player_to_sync):
        self.sonos_player.group.coordinator.join(soco.discovery.by_name(name_of_sonos_player_to_sync))

    async def set_alarm(self, type, volume):
        super().set_alarm(type, volume)
        if type == "bell":
            snapshotclass = snapshot.Snapshot(self.sonos_player, snapshot_queue=False)
            snapshotclass.snapshot()
            # self.sonos_player.play_uri("aac://http://stream-uk1.radioparadise.com/aac-320")
            # self.sonos_player.play_uri("x-file-cifs://10.1.10.90/static/bell.wav")
            await asyncio.sleep(1)
            # snapshotclass.restore()
        elif type == "alarm":
            pass  # TODO: Implement alarm
        elif type == "firealarm":
            pass  # TODO: Implement firealarm
        elif type == "wecker":
            pass  # TODO: Implement wecker

    def get_name(self):
        return self.sonos_player.player_name

    def get_str(self):
        return super().get_str()

    def get_queue(self):
        queue = self.sonos_player.group.coordinator.get_queue()
        queue_list = {}
        queue_list["total"] = len(queue)
        queue_list["items"] = []
        for item in queue:
            queue_list["items"].append(
                {
                    "id": item.resources[0].uri,
                    "title": item.title,
                    "image": item.album_art_uri,
                }
            )
        return queue_list

    async def tts(self, lang_and_message, volume):
        old_volume = self.sonos_player.volume
        relative_path_to_file = await super().tts(lang_and_message, volume)
        snapshotclass = snapshot.Snapshot(self.sonos_player, snapshot_queue=False)
        snapshotclass.snapshot()
        self.set_volume(volume)
        self.sonos_player.group.coordinator.play_uri(f"http://10.1.10.90:8091/{relative_path_to_file}")
        await asyncio.sleep(10)
        snapshotclass.restore()
        self.set_volume(old_volume)

    def _time_str_to_milliseconds(self, time_str):
        if time_str == "NOT_IMPLEMENTED":
            return 0
        hours, minutes, seconds = map(int, time_str.split(":"))
        return (hours * 3600 + minutes * 60 + seconds) * 1000

    def _mode_sonos_to_loxone(self, mode):
        if mode == "PLAYING":
            return "play"
        elif mode == "PAUSED_PLAYBACK":
            return "pause"
        elif mode == "STOPPED":
            return "stop"
        elif mode == "TRANSITIONING":
            return "buffer"
        else:
            # Should never happen but just in case :)
            return "stop"

    def _repeat_sonos_to_loxone(self, repeat):
        if repeat == False:
            return 0
        elif repeat == "ONE":
            return 1
        elif repeat == True:
            return 2
        else:
            # Should never happen but just in case :)
            return 0

    async def __update_info(self):
        while True:
            track_info = self.sonos_player.group.coordinator.get_current_track_info()
            transport_info = self.sonos_player.group.coordinator.get_current_transport_info()

            self.track.id = track_info["uri"]
            self.track.title = track_info["title"]
            self.track.album = track_info["album"]
            self.track.artist = track_info["artist"]
            self.track.duration = self._time_str_to_milliseconds(track_info["duration"])
            self.track.image = track_info["album_art"]

            self.player.id = self.sonos_player.uid
            self.player.mode = self._mode_sonos_to_loxone(transport_info["current_transport_state"])
            self.player.set_time(self._time_str_to_milliseconds(track_info["position"]))
            self.player.volume = self.sonos_player.volume
            self.player.repeat = self._repeat_sonos_to_loxone(self.sonos_player.group.coordinator.repeat)
            self.player.shuffle = int(self.sonos_player.group.coordinator.shuffle)

            if self.player.mode == "play":
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(5)
