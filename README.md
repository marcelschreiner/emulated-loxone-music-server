[![HitCount](https://hits.dwyl.com/marcelschreiner/emulated-loxone-music-server.svg?style=flat)](http://hits.dwyl.com/marcelschreiner/emulated-loxone-music-server)

# Emulated Loxone Music Server

This project aims to integrate Sonos and Chromecast speakers into the Loxone universe.
The goal is to support as many as possible of the native features a Loxone Music Server would offer.
To achieve this, the interface of a music server is emulated. As far as the Loxone Miniserver is concerned, it thinks that it is talking to a regular music server.

> [!NOTE]
> This is the latest of my projects and it is still under development. Thus... not everything works reliably. 🤓

The following table aims to give an overview of the functions the Music Server Supports and which of them are already implemented.

| URL Pattern | Description | Sonos Integration | Chomecast integration
|-------------|-------------|-------------------|-----------------------|
| `/audio/cfg/all` | Audio configuration for all devices |  |  |
| `/audio/cfg/equalizer/` | Audio configuration for equalizer |  |  |
| `/audio/cfg/favorites/addpath/` | Add path to audio favorites |  |  |
| `/audio/cfg/getfavorites/` | Get audio favorites |  |  |
| `/audio/cfg/getinputs` | Get audio inputs |  |  |
| `/audio/cfg/getkey` | Get public key |  |  |
| `/audio/cfg/getmediafolder` | Get media folder |  |  |
| `/audio/cfg/getmaster` | Get master device |  |  |
| `/audio/cfg/getplayersdetails` | Get details of all players |  |  |
| `/audio/cfg/getplaylists2/lms` | Get playlists |  |  |
| `/audio/cfg/getradios` | Get radio stations |  |  |
| `/audio/cfg/getroomfavs/` | Get room favorites |  |  |
| `/audio/cfg/getservices` | Get available services |  |  |
| `/audio/cfg/getsyncedplayers` | Get synced players |  |  |
| `/audio/cfg/iamaminiserver/` | Declare as a mini server | ✅ | ✅ |
| `/audio/cfg/input/[input]/rename/` | Rename an input |  |  |
| `/audio/cfg/input/[input]/type/` | Set type of an input |  |  |
| `/audio/cfg/mac` | Get MAC address | ✅ | ✅ |
| `/audio/cfg/playlist/create` | Create a playlist |  |  |
| `/audio/cfg/scanstatus` | Get scan status |  |  |
| `/audio/cfg/getmonitorstatus` | Get monitor status |  |  |
| `/audio/[id]/alarm/` | Set alarm |  |  |
| `/audio/[id]/favoriteplay` | Play favorite |  |  |
| `/audio/[id]/getqueue` | Get queue | ✅ |  |
| `/audio/[id]/identifysource` | Identify source |  |  |
| `/audio/[id]/library/play` | Play from library |  |  |
| `/audio/[id]/linein` | Line in |  |  |
| `/audio/[id]/off` | Turn off |  |  |
| `/audio/[id]/on` | Turn on |  |  |
| `/audio/[id]/pause` | Pause | ✅ | ✅ |
| `/audio/[id]/play` | Play | ✅ | ✅ |
| `/audio/[id]/playlist/` | Play playlist |  |  |
| `/audio/[id]/position/[position]` | Set position | ✅ | ✅ |
| `/audio/[id]/queueminus` | Go to last song | ✅ | ✅ |
| `/audio/[id]/queueplus` | Go to next song | ✅ | ✅ |
| `/audio/[id]/repeat/[repeat]` | Set repeat |  |  |
| `/audio/[id]/roomfav/delete/[id]` | Delete room favorite |  |  |
| `/audio/[id]/roomfav/play/[id]` | Play room favorite |  |  |
| `/audio/[id]/roomfav/plus` | Add room favorite |  |  |
| `/audio/[id]/roomfav/savepath/[id]/` | Save path as room favorite |  |  |
| `/audio/[id]/serviceplay/` | Play service |  |  |
| `/audio/[id]/shuffle/[shuffle]` | Set shuffle | ✅ |  |
| `/audio/[id]/sync/[id]/` | Sync devices | ✅ |  |
| `/audio/[id]/volume/[volume]` | Set volume | ✅ | ✅ |

In this table, [id] is a placeholder for the ID of an audio zone.


This project is based on the awesome work by [mjesun](https://github.com/mjesun) and his [loxberry-music-server-gateway](https://github.com/mjesun/loxberry-music-server-gateway)


# README mjesun/loxberry-music-server-gateway

## Motivation

To enable plugin developers to create their own customizations with the music
server, this plugin proxies you calls about things that happen in the Loxone
UI. You receive calls by creating an HTTP server that will have to respond to
certain calls.

This plugin takes care of:

- Managing the connection to the Miniserver and the Loxone UI, as well as the
  authentication protocol.

- Converts the protocol used by the UI and the Loxone Miniserver into standard,
  HTTP calls (not all parts work the same way internally).

- Publicly documenting all possibilities.


## Service endpoints

The fake server runs in port `7090`, and each Music Server created will run on a
consecutive port. Thus the first Music Server will run in port `7091`, which
is the default port used by Loxone Miniserver. The server contains a variety of
endpoints (and a WebSocket) used by the Loxone Miniserver and the UI to
communicate with it. Other endpoints worth noting are:

- `/restart`: useful for restarting the service. Accepts a `code` parameter
  through query string, with the following values:

  - `0`: the service finishes cleanly.
  - `254`: immediately restart the service.

  Any other code will restart the service after 5 seconds.

_All of these ports (`7090`, `7091`), etc. are for internal management and
communication with the Loxone Miniserver, and they have nothing to do with the
public interface exposed by this plugin. To enable you reading the actions that
come from the Loxone UI, please keep reading._

## Communication

You first need to point the plugin to your HTTP server. Creating a server is
easy in the majority of languages. For instance, in Node.js you can do:

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  console.log(req.method + ' ' + req.url);

  res.writeHead(404);
  res.end();
});

server.listen(8091);
```

You can pick any language you want; even an Apache server + PHP would do the
trick.

Once you are running your own HTTP server, you will start receiving calls.
Those calls vary depending on the actions you perform in the UI. In general,
you can reply with an HTTP code `404` to indicate you don't want to handle that
particular call, and the server will do "the right thing" for you (usually
sending back empty lists, etc).

All HTTP actions issued by the plugin to your server are expected to be
received in the shape of JSON.

### Data format

The music server divides the experience into zones. Each zone is identified by
an identifier. Zones start being numbered from `1` to match Loxone's numbering.
Each zone contains an internal status that looks like the follwoing:

```javascript
{
  "player": {
    "id": string, // Opaque identifier, you can pass anything you want.
    "mode": "play" | "buffer" | "pause" | "stop",
    "time": number, // In milliseconds.
    "volume": number, // [0, 100] range for volume (0 = muted, 100 = maximum).
    "repeat": 0 | 1 | 2, // Repeat mode (0 = none, 1 = track, 2 = context).
    "shuffle: 0 | 1, // Shuffle mode (0 = not shuffled, 1 = shuffled).
  },
  "track": {
    "id": string, // Opaque identifier, you can pass anything you want.
    "title": string,
    "album": string,
    "artist": string,
    "duration": number, // In milliseconds.
    "image": string, // Usually the cover URL, but you can also pass an SVG.
  },
}
```

The `player.id` differs from the `track.id` in the sense that the `player` one
represents the queue being played, while the `track` one is a particular track.
For instance, if you were playing a playlist called "Big Hits", and the track
playing was "Never Gonna Give You Up", `player.id` would represent "Big Hits"
(the whole playlist), while `track.id` just the song. So, when a track finishes
playing, `track.id` will change, but not `player.id`; until you play a new
context from scratch.

To pass an SVG as an icon, use the `data:` protocol. First base-64 encode your
icon, then prepend: `data:image/svg+xml;base64,`.

### Lists

A large amount of sections of the API use lists to identify elements. Thus,
lists have a generic interface. This interface is meant to return fragments of
the list:

```javascript
{
  "total": number, // Total amount of elements in the list.
  "items": [
    {
      "id": string, // Opaque identifier, you can pass anything you want.
      "title": string,
      "image": string, // Usually the cover URL, but you can also pass an icon.
    },
  ],
```

Note how list and track interface naming are carefully picked, so that you can
return a track object within an item list and fulfill its requirements. In
fact, extra keys are ignored and do not constitute an issue.

All lists follow a common interface:

- `GET` `/:position`: returns the list of elements starting from the given
  position in the `position` query parameter. The amount of items returned can
  be picked by the implementor.

- `POST` `/:position`: adds one or more items _before_ the given position. In
  other words, the position passed is the one that the first new item will occupy.
  Items will be passed as part of the body of the HTTP call, in the shape of
  a JSON array. You can know which items were added by checking their `id`.

- `PUT` `/:position`: replaces one or more items starting from the given
  position.

- `DELETE` `/:position/:length`: removes the items stored in place starting
  from the position given.

### Basic player control

Your server can receive the following HTTP calls regarding player (zone)
control. All of them are `POST`, except the first one:

- `/zone/:zone/state`: returns the state of the zone, as described in the upper
  section (this call is a `GET`).

- `/zone/:zone/play/:contentId`: start playing on the given zone the provided
  content.

- `/zone/:zone/pause`: pause the given zone.

- `/zone/:zone/time/:time`: seek to the corresponding time.

- `/zone/:zone/volume/:volume`: set the volume of the given zone. Volume
  parameters go from 0 to 100 (from mute to hightest possible volume). Volume
  stepping (when using + or - from the UI) is controlled by the Loxone module.

- `/zone/:zone/repeat/:mode`: mode can be `0` for non-repeated, `1` for
  repeating one track, and `2` for repeating mutliple tracks.

- `/zone/:zone/shuffle/:mode`: mode can be `0` for non-shuffled, and `1` for
  shuffled playing.

- `/zone/:zone/previous`: move to the previous track. The internal server
  implements a control where touching "previous" track will send a
  `zone/:zone/time/0` unless the current time is below 3 seconds.

- `/zone/:zone/next`: move to the next track.

### Advanced player control

- `/equalizer`: used to set and retrieve the configuration for the equalizer.
  The format is returned in a 10-band ISO compliant array, where each value is
  within a `[-10, +10]` range. To get the setting the verb used is a `GET`; and
  to update it, a `PUT`.

- `/zone/:zone/alarm/:type/:volume`: an alarm has been requested to play. Type
  can be one of `general`, `bell`, `clock` or `fire`. Volume establishes at
  what volume it has to be played. Expected to obtain back the player state.

Each of these should respond with the zone status _after_ executing the call.
For instance, `/zone/1/pause` should respond with a `state` of `"pause"` even
if the internal player hasn't paused yet. This enables accurate synchronization
between the UI and the players.

### Favorites

- `/zone/:zone/favorites`: list interface for the zone favorites. A maximum of 8
  is shown. While the zone UI can deal with more, the configurator gets
  confused.

- `/favorites`: list interface for the global favorites.

### Other lists

- `/zone/:zone/queue`: queue of tracks being played.

- `/playlists`: list interface for all the existing playlists.

- `/library`: list interface for the complete library.

- `/inputs`: list interface for the external inputs. Inputs can configure their
  icon from the Loxone UI, so a specific set of values is allowed / read from
  those (listed by order of appearance in the UI):

  - `line-in`
  - `cd-player`
  - `computer`
  - `i-mac`
  - `i-pod`
  - `mobile`
  - `radio`
  - `tv`
  - `turntable`

  When the icon is updated you will get a `PUT` call for the same item, and the
  new icon name.

## Favorite identification

The music zone module contains an `AQs` output that informs about the favorite
being played. This output is (ab)used by the gateway, to provide information
not only about the favorite position being played, but also about other sources
of data. The number being output is formed in the following way:

```
SPPPPPP
```

- `S`: this is the source identifier. The following sources are recognized:

  - `0`: unknown source is playing (e.g. playback started from another origin).
  - `1`: zone favorite playing.
  - `2`: global favorite playing.
  - `3`: playlist playing.
  - `4`: library item playing.
  - `5`: external input playing.

- `PPPPPP`: this is the position identifier, which ranges from 0 to 999,999
  items. Behavior for lists over a million elements is undetermined.

Remember all indices are 0-based; so playing the third zone favorite will be
identified as `1000002`. You can unroll this information by using a "Divide"
and "Modulo" blocks:

![AQs output](./docs/AQs-output.png)

You will need to make both `AI2` inputs to contain the static value `1000000`
(one milion). You will then get the `S` value in the `AQ` output of the
"Divide" block, and the `PPPPPP` value in the `AQ` output of the "Modulo"
block.

## Events

You can inform the gateway about changes that are produced externally by
relying on an [SSE (Server-Sent
Events)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Sending_events_from_the_server)
interface. The gateway tries connecting to the `/events` endpoint, where you
can push the path (URI) that you want to make the gateway refresh. For
instance:

- To make the gateway refresh the state of a player, use `/zone/:zoneId/state`.
- To refresh the list of favorites use `/favorites/0`.
- To refresh the list of inputs starting from the third one, use `/inputs/3`.

The gateway will immediately invalidate the internal data, re-request it, then
inform the Loxone UI about the new data. Notice how this is an add-on over the
gateway protocol; you do not have to implement it if you don't want, nor you
have to modify exising code if you want to support it.

This endpoint also supports long-polling if you don't want to implement SSE.
You just hold the HTTP connection until you've got an update you would like
pushing.
