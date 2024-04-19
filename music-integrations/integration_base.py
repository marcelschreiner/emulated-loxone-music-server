from datetime import datetime, timedelta
import os
from gtts import gTTS, lang


class TTS:
    @staticmethod
    def _loxone_lang_to_gtts_lang(loxone_lang):
        # Loxone supported languages
        conversion = {
            "DEU": "de",  # German
            "cz": "cs",  # Czech
            "en": "en",  # British English
            "us": "en",  # American English
            "es": "es",  # Spanish
            "fi": "fi",  # Finnish
            "fr": "fr",  # French
            "hu": "hu",  # Hungarian
            "it": "it",  # Italian
            "nl": "nl",  # Dutch
            "pl": "pl",  # Polish
            "ru": "ru",  # Russian
            "tr": "tr",  # Turkish
            "pt": "pt",  # Portuguese
            "cat": "ca",  # Catalan
            "se": "sv",  # Swedish
            "cn": "zh",  # Chinese
        }
        if loxone_lang in conversion:
            return conversion[loxone_lang]
        else:
            return "en"

    @staticmethod
    def generate_mp3(lang_and_message):
        language, message = lang_and_message.split("|", 1)
        tts = gTTS(message, lang=TTS._loxone_lang_to_gtts_lang(language))
        timestamp_milli = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        filename = f"{current_file_path}/../music-files/tts_{timestamp_milli}.mp3"
        relative_filename = f"static/tts_{timestamp_milli}.mp3"
        tts.save(filename)
        return relative_filename


class Player:
    def __init__(self):
        self.id = ""  # Opaque identifier, you can pass anything you want.
        self.mode = "stop"  # "play" | "buffer" | "pause" | "stop"
        self.__time_start = datetime.now()
        self.__time_current = 0
        self.volume = 0  # [0, 100] range for volume (0 = muted, 100 = maximum)
        self.repeat = 0  # Repeat mode (0 = none, 1 = track, 2 = context)
        self.shuffle = 0  # Shuffle mode (0 = not shuffled, 1 = shuffled)

    def set_time(self, time: int):
        """Set the current time of the player in milliseconds."""
        time = int(time)
        self.__time_start = datetime.now() - timedelta(seconds=time / 1000)
        self.__time_current = time

    def get_time(self):
        """Get the current time of the player in milliseconds."""
        if self.mode == "play":
            return int((datetime.now() - self.__time_start).total_seconds()) * 1000
        else:
            return self.__time_current

    def get_str(self):
        if self.mode == "play":
            self.time = int((datetime.now() - self.__time_start).total_seconds() * 1000)
        else:
            self.time = 0
        return {
            "id": self.id,
            "mode": self.mode,
            "time": self.get_time(),  # In milliseconds
            "volume": self.volume,
            "repeat": self.repeat,
            "shuffle": self.shuffle,
        }


class Track:
    def __init__(self):
        self.id = ""  # Opaque identifier, you can pass anything you want
        self.title = ""
        self.album = ""
        self.artist = ""
        self.duration = 0  # In milliseconds
        self.image = ""  # Usually the cover URL, but you can also pass an SVG

    def get_str(self):
        return {
            "id": self.id,
            "title": self.title,
            "album": self.album,
            "artist": self.artist,
            "duration": self.duration,
            "image": self.image,
        }


class MusicZoneBase:
    def __init__(self):
        self.player = Player()
        self.track = Track()

    def play(self):
        self.player.mode = "play"

    def pause(self):
        self.player.mode = "pause"

    def stop(self):
        self.player.mode = "stop"

    def next(self):
        pass

    def previous(self):
        pass

    def set_volume(self, volume):
        self.player.volume = volume

    def set_repeat(self, repeat):
        self.player.repeat = repeat

    def set_shuffle(self, shuffle):
        self.player.shuffle = shuffle

    def set_time(self, time):
        self.player.set_time(time)

    def set_alarm(self, type, volume):
        self.player.volume = volume

    def get_name(self):
        return ""

    def get_equalizer(self):
        # Return the equalizer settings in JSON format
        # (10 bands, -10..10 range, 31Hz, 63Hz, 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, 4kHz, 8kHz, 16kHz)
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def get_favorites(self):
        favorites = {
            "total": 5,  # Total amount of elements in the list.
            "items": [
                {
                    "id": "Artists",  # Opaque identifier, you can pass anything you want.
                    "title": "Artists",
                    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="100%" height="100%" fill="black"/><title>account</title><path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" /></svg>',  # Usually the cover URL, but you can also pass an icon.
                },
                {
                    "id": "Albums",  # Opaque identifier, you can pass anything you want.
                    "title": "Albums",
                    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>album</title><rect width="100%" height="100%" fill="black"/><path d="M12,11A1,1 0 0,0 11,12A1,1 0 0,0 12,13A1,1 0 0,0 13,12A1,1 0 0,0 12,11M12,16.5C9.5,16.5 7.5,14.5 7.5,12C7.5,9.5 9.5,7.5 12,7.5C14.5,7.5 16.5,9.5 16.5,12C16.5,14.5 14.5,16.5 12,16.5M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" /></svg>',
                },
                {
                    "id": "Genres",  # Opaque identifier, you can pass anything you want.
                    "title": "Genres",
                    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>earth</title><rect width="100%" height="100%" fill="black"/><path d="M17.9,17.39C17.64,16.59 16.89,16 16,16H15V13A1,1 0 0,0 14,12H8V10H10A1,1 0 0,0 11,9V7H13A2,2 0 0,0 15,5V4.59C17.93,5.77 20,8.64 20,12C20,14.08 19.2,15.97 17.9,17.39M11,19.93C7.05,19.44 4,16.08 4,12C4,11.38 4.08,10.78 4.21,10.21L9,15V16A2,2 0 0,0 11,18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" /></svg>',
                },
                {
                    "id": "Songs",  # Opaque identifier, you can pass anything you want.
                    "title": "Songs",
                    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>music-note</title><rect width="100%" height="100%" fill="black"/><path d="M12 3V13.55C11.41 13.21 10.73 13 10 13C7.79 13 6 14.79 6 17S7.79 21 10 21 14 19.21 14 17V7H18V3H12Z" /></svg>',
                },
                {
                    "id": "Playlists",  # Opaque identifier, you can pass anything you want.
                    "title": "Playlists",
                    "image": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>playlist-music</title><rect width="100%" height="100%" fill="black"/><path d="M15,6H3V8H15V6M15,10H3V12H15V10M3,16H11V14H3V16M17,6V14.18C16.69,14.07 16.35,14 16,14A3,3 0 0,0 13,17A3,3 0 0,0 16,20A3,3 0 0,0 19,17V8H22V6H17Z" /></svg>',
                },
            ],
        }
        return favorites

    def get_queue(self):
        queue = {
            "total": 0,  # Total amount of elements in the list.
            "items": [],
        }
        return queue

    def get_str(self):
        return {"player": self.player.get_str(), "track": self.track.get_str()}

    async def tts(self, lang_and_message, volume):
        return TTS.generate_mp3(lang_and_message)
