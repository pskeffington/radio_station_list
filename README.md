# Radio Station List

Public, versioned source catalog for the **Sagamore Soundworks Rust internet radio client**. This repository is the station-data backend. The separate [Sagamore Soundworks app](https://github.com/pskeffington/sagamore-sound) fetches its station list over HTTPS and caches the last validated manifest.

## Canonical client feed

~~~
https://raw.githubusercontent.com/pskeffington/radio_station_list/main/stations/v1.tsv
~~~

View the [station catalog](stations/v1.tsv) or the [station evidence register](SOURCES.md).

## Schema: sagamore-stations-v1

UTF-8, tab-separated lines; the first two lines are mandatory. There is one radio station per record:

~~~tsv
# sagamore-stations-v1
id	name	url	country	genre
skylab-uk	Skylab Radio (UK)	https://uksoutha.streaming.broadcast.radio:29690/skylab-radio-limited	GB	Ambient / chillout / lounge
~~~

- id: unique lowercase ASCII slug, maximum 64 characters; stable across updates
- name: display text, maximum 120 characters, no tabs or newlines
- url: direct, publicly accessible HTTP(S) playable audio stream; HTTPS preferred; maximum 2048 characters; no credentials
- country: ISO 3166-1 alpha-2 country code (e.g. GB)
- genre: human-readable category, maximum 80 characters
- No JSON/parser dependencies are needed in the Rust client.
- Up to 2,000 stations; 256 KiB hard limit on manifest size.
- Format changes require a new versioned file, such as stations/v2.tsv. Preserve v1 compatibility while supported clients use it.

The stream endpoint is *not* a playlist/website landing page. Do not substitute a station's marketing website for the stream URL. Playback is delegated to the app's local audio backend.

## Contributing and validation

1. Confirm the station's identity and country from the broadcaster's own website; distinguish same-name broadcasters.
2. Resolve a direct public stream, preferring a broadcaster-published link. Record provenance in [SOURCES.md](SOURCES.md).
3. Add or update one row in stations/v1.tsv, preserving stable id and tab delimiters.
4. Run: `python3 scripts/validate_catalog.py stations/v1.tsv`.
5. Submit a PR; CI validates schema and performs unit tests before review.
6. Verify actual network response and audible output on an audio-equipped device before marking a station operational. Syntax validation does **not** prove stream health.

**Privacy/licensing:** The catalog consists of factual station links, not streams, recordings, logos, station software or redistributed broadcasts. Respect each broadcaster's terms and rights. Never commit station credentials, tokens, or private stream endpoints.

## Consumer behavior

The Rust app reads the public feed using HTTPS, caches the last valid result, and falls back to its existing local catalog when offline. Local user presets may override a specific catalog entry. Registry updates do not require recompiling the app. The catalog is a content feed, **not** a streaming proxy.
