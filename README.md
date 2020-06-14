# spotify-duplicates

Resolve duplicate Spotify songs through your terminal :headphones:

## Why

Often you find yourself with multiple instances of the same song in different playlists which can be undesirable, and there is no way to deal with that inside Spotify. The Python script `duplicates.py` combats this by comparing songs by name in all playlists, this way same tracks from different albums are also found.

## Demo

[![showcase](https://asciinema.org/a/V2qepxMcR51eH988yQxzMMZDz.svg)](https://asciinema.org/a/V2qepxMcR51eH988yQxzMMZDz)

## Installation

```
git clone https://github.com/deinal/spotify-duplicates.git
cd spotify-duplicates
pip install -r requirements.txt
```

## Authenticate with Spotify

- Log in to https://developer.spotify.com/dashboard
- Create an app on the dashboard, remember to set a callback url, e.g. `http://localhost:8888/callback`
- Copy `Client ID` and `Client Secret` to a `.env` file in the root of the project.

Example `.env`:
```
SPOTIFY_ID='Client ID'
SPOTIFY_SECRET='Client Secret'
SPOTIFY_REDIRECT='http://localhost:8888/callback'
```

## Usage

### Get your Spotify user id

An easy way: go to your `Profile` on the spotify app, press the `Three dots` and `Share` to get a link like this `https://open.spotify.com/user/<spotify_user_id>` where the last part is your user id.

### Run

Removal happens by choosing with the number keys for each duplicate song, a space separated integer list is also accepted when you want to remove multiple tracks.

Remove duplicates
```
python duplicates.py --user <spotify_user_id>
```

Only list duplicates
```
python duplicates.py --user <spotify_user_id> --list
```

Help
```
python duplicates.py --help
```
