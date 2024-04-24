from homeassistant_api import Client
from integration_base import MusicZoneBase
import asyncio


class MusicZoneHA(MusicZoneBase):
    @staticmethod
    def set_credentials(api_url, token):
        MusicZoneHA.api_url = api_url
        MusicZoneHA.token = token

    def __init__(self, entity_id_of_ha_player):
        super().__init__()
        self.client = Client(api_url=MusicZoneHA.api_url, token=MusicZoneHA.token, cache_session=False)
        self.entity = self.client.get_entity(entity_id=entity_id_of_ha_player)
        self.media_player = self.client.get_domain("media_player")
        self.entity_id = entity_id_of_ha_player
        loop = asyncio.get_event_loop()
        loop.create_task(self.__update_info())

    def play(self):
        super().play()
        self.media_player.media_play(entity_id=self.entity_id)

    def pause(self):
        super().pause()
        self.media_player.media_pause(entity_id=self.entity_id)

    def stop(self):
        super().stop()
        self.media_player.media_stop(entity_id=self.entity_id)

    def next(self):
        super().next()
        self.media_player.media_next_track(entity_id=self.entity_id)

    def previous(self):
        super().previous()
        self.media_player.media_previous_track(entity_id=self.entity_id)

    def set_volume(self, volume):
        super().set_volume(volume)
        self.media_player.volume_set(entity_id=self.entity_id, volume_level=volume / 100)

    def set_time(self, time):
        super().set_time(time)
        self.media_player.media_seek(entity_id=self.entity_id, seek_position=time / 1000)

    def set_repeat(self, repeat):
        super().set_repeat(repeat)
        # Repeat mode (0 = none, 1 = track, 2 = context)
        if repeat == 0:
            self.media_player.repeat_set(entity_id=self.entity_id, repeat="off")
        elif repeat == 1:
            self.media_player.repeat_set(entity_id=self.entity_id, repeat="one")
        elif repeat == 2:
            self.media_player.repeat_set(entity_id=self.entity_id, repeat="all")

    def set_shuffle(self, shuffle):
        super().set_shuffle(shuffle)
        # Shuffle mode (0 = not shuffled, 1 = shuffled)
        self.media_player.shuffle_set(entity_id=self.entity_id, shuffle=shuffle)

    def set_sync(self, entity_id_to_sync):
        self.media_player.join(entity_id=self.entity_id, group_members=[entity_id_to_sync])

    async def set_alarm(self, type, volume):
        super().set_alarm(type, volume)
        if type == "bell":
            # https://10.1.10.90/static/bell.wav
            pass  # TODO: Implement bell
        elif type == "alarm":
            pass  # TODO: Implement alarm
        elif type == "firealarm":
            pass  # TODO: Implement firealarm
        elif type == "wecker":
            pass  # TODO: Implement wecker

    def get_name(self):
        return self.entity_id

    def get_str(self):
        return super().get_str()

    def get_queue(self):
        return super().get_queue()

    async def tts(self, lang_and_message, volume):
        # TODO: Implement TTS
        pass

    def _mode_ha_to_loxone(self, mode):
        if mode in ["playing"]:
            return "play"
        elif mode in ["paused"]:
            return "pause"
        elif mode in ["idle", "off", "on", "standby"]:
            return "stop"
        elif mode in ["buffering"]:
            return "buffer"
        else:
            # Should never happen but just in case :)
            return "stop"

    def _repeat_ha_to_loxone(self, repeat):
        if repeat == "off":
            return 0
        elif repeat == "one":
            return 1
        elif repeat == "all":
            return 2
        else:
            # Should never happen but just in case :)
            return 0

    def _get_if_available(self, state, attribute, default):
        if attribute in state.attributes:
            return state.attributes[attribute]
        else:
            return default

    async def __update_info(self):
        while True:
            state = self.client.get_state(entity_id=self.entity_id)

            self.track.id = self._get_if_available(state, "media_content_id", "")
            self.track.title = self._get_if_available(state, "media_title", "")
            self.track.album = self._get_if_available(state, "media_album_name", "")
            self.track.artist = self._get_if_available(state, "media_artist", "")
            self.track.duration = self._get_if_available(state, "media_duration", 0) * 1000
            self.track.image = MusicZoneHA.api_url.replace("/api", "") + self._get_if_available(
                state, "entity_picture", ""
            )

            self.player.id = self._get_if_available(state, "media_content_id", "")
            self.player.mode = self._mode_ha_to_loxone(state.state)
            self.player.set_time(self._get_if_available(state, "media_position", 0) * 1000)
            self.player.volume = int(self._get_if_available(state, "volume_level", 0) * 100)
            self.player.repeat = self._repeat_ha_to_loxone(self._get_if_available(state, "repeat", "off"))
            self.player.shuffle = int(self._get_if_available(state, "shuffle", False))

            if self.player.mode == "play":
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(5)
