from integration_sonos import MusicZoneSonos
from integration_cast import MusicZoneCast
from integration_base import MusicZoneBase
import asyncio
from aiohttp import web
from subprocess import Popen
import sys
import os
import json

zones = [None] * 20

# Manually define the zones
zones[0] = MusicZoneSonos("Schlafzimmer")
zones[1] = MusicZoneSonos("Schreibtisch")
zones[2] = MusicZoneSonos("Bad")
zones[3] = MusicZoneSonos("Balkon")
zones[4] = MusicZoneCast("Heimkino")
zones[5] = MusicZoneCast("Wohnzimmer")
zones[6] = MusicZoneCast("Wonzimmer TV")
zones[7] = MusicZoneCast("Küche")
zones[8] = MusicZoneCast("Erker")
zones[9] = MusicZoneCast("Arbeitszimmer")
zones[10] = MusicZoneBase()
zones[11] = MusicZoneBase()
zones[12] = MusicZoneBase()
zones[13] = MusicZoneBase()
zones[14] = MusicZoneBase()
zones[15] = MusicZoneBase()
zones[16] = MusicZoneBase()
zones[17] = MusicZoneBase()
zones[18] = MusicZoneBase()
zones[19] = MusicZoneBase()


def is_zone_id_valid(zone_id):
    return zone_id >= 0 and zone_id < len(zones) and zones[zone_id] is not None


async def run_server_gateway():
    while True:
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        p = Popen(["node", f"{current_file_path}/../music-server/index.js"])

        while True:
            await asyncio.sleep(5)
            result = p.poll()

            if result == 0:
                # Quit the whole script
                sys.exit(0)

            if result == 25:
                # Restart the node server
                break

            if result is None:
                # Process is still running
                await asyncio.sleep(5)


async def handle_action(request):
    # print(f"Action: {request.method} {request.match_info.get('zone_id')} {request.match_info.get('action')}")
    zone_id = int(request.match_info["zone_id"]) - 1
    if is_zone_id_valid(zone_id):
        if request.method == "GET":
            action = request.match_info["action"]
            if action == "equalizer":
                return web.Response(text=json.dumps(zones[zone_id].get_equalizer()), content_type="application/json")
            elif action == "state":
                return web.Response(text=json.dumps(zones[zone_id].get_str()), content_type="application/json")

        if request.method == "POST":
            action = request.match_info["action"]
            if action == "resume":
                zones[zone_id].play()
            elif action == "pause":
                zones[zone_id].pause()
            elif action == "stop":
                zones[zone_id].stop()
            elif action == "next":
                zones[zone_id].next()
            elif action == "previous":
                zones[zone_id].previous()
            elif action == "equalizer":
                equalizer = zones[zone_id].get_equalizer()
                print(equalizer)
                return web.Response(text=equalizer, content_type="application/json")
            else:
                return web.HTTPNotFound()
            return web.HTTPSuccessful()
    return web.HTTPNotFound()


async def handle_action_with_value(request):
    print(
        f"Action: {request.method} {request.match_info.get('zone_id')} {request.match_info.get('action')} value={request.match_info.get('value')}"
    )
    zone_id = int(request.match_info["zone_id"]) - 1
    action = request.match_info["action"]
    value = request.match_info["value"]

    return_value = None

    if is_zone_id_valid(zone_id):
        if action == "volume":
            zones[zone_id].set_volume(int(value))
        elif action == "time":
            zones[zone_id].set_time(int(value))
        elif action == "repeat":
            zones[zone_id].set_repeat(int(value))
        elif action == "shuffle":
            zones[zone_id].set_shuffle(int(value))
        elif action == "sync":
            zone_id_sync = int(value) - 1
            # Ignore sync if the zones are not the same type
            if type(zones[zone_id]) == type(zones[zone_id_sync]):
                zones[zone_id].set_sync(zones[zone_id_sync].get_name())
        elif action == "queue":
            return_value = zones[zone_id].get_queue()
        elif action == "favorites":
            return_value = zones[zone_id].get_favorites()
        elif action == "alarm":
            await zones[zone_id].set_alarm(value, int(request.match_info["value2"]))
        elif action == "tts":
            await zones[zone_id].tts(value, int(request.match_info["value2"]))
        else:
            return web.HTTPNotFound()

        if return_value is not None:
            return web.Response(text=json.dumps(return_value), content_type="application/json")
        return web.HTTPSuccessful()
        # return web.Response(text=json.dumps(zones[zone_id].player.get_str()), content_type="application/json")


async def handle_file(request):
    filename = request.match_info.get("filename", "index.html")  # Default to "index.html" if no filename is provided
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music-files", filename)
    if os.path.exists(filepath) is False:
        return web.HTTPNotFound()
    return web.FileResponse(path=str(filepath))


app = web.Application()
app.router.add_route("*", "/zone/{zone_id}/{action}", handle_action)
app.router.add_route("*", "/zone/{zone_id}/{action}/{value}", handle_action_with_value)
app.router.add_route("*", "/zone/{zone_id}/{action}/{value}/{value2}", handle_action_with_value)
app.router.add_route("*", "/static/{filename}", handle_file)
# app.router.add_route('*', '/library/0', handle_library)

loop = asyncio.get_event_loop()

loop.create_task(run_server_gateway())
loop.create_task(web._run_app(app, port=8091))

try:
    loop.run_forever()
except KeyboardInterrupt as e:
    print("Exiting")
    sys.exit(0)
