import os
import sys
import spotipy
import spotipy.util as util
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name']))

def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return ((key, locs) for key, locs in tally.items() if len(locs) > 1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Whoops, need your username!")
        print("usage: python duplicates.py <username>")
        sys.exit()

    token = util.prompt_for_user_token(username,
                    client_id=os.getenv('SPOTIFY_ID'),
                    client_secret=os.getenv('SPOTIFY_SECRET'),
                    redirect_uri=os.getenv('SPOTIFY_REDIRECT'))

    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.current_user_playlists()
        
        n = 0
        names = []
        songs = {}
        print("Your playlists:")

        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:

                print(playlist['name'], 'Total tracks:', playlist['tracks']['total'])

                results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = results['tracks']

                for i, item in enumerate(tracks['items']):
                    track = item['track']
                    songs[n] = {'playlist': playlist['name'], '#': i}
                    names.append(track['name'])
                    n = n + 1

        names = [x for x in names if x is not None]

        print("\nYour duplicates:")
        print(f"{'Song':70s}{'Playlist':20s}#")
        for name, dup in sorted(list_duplicates(names)):
            for n in dup:
                print(f"{name:70s}{songs[n]['playlist']:20s}{songs[n]['#']}")

    else:
        print("Can't get token for", username)
