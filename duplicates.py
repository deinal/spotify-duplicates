import os
import sys
import argparse
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
    print('                       __  .__  _____                    .___           .__  .__               __                  ')
    print('  ____________   _____/  |_|__|/ ____\__.__.           __| _/_ ________ |  | |__| ____ _____ _/  |__  ____   ______ ')
    print(' /  ___/\____ \ /  _ \   __\  \   __|   |  |  ______  / __ |  |  \____ \|  | |  |/ ___\\\\__  \\\\    __|/ __ \ /  ___/')
    print(' \___ \ |  |_| |  |_| )  | |  ||  |  \___  | /_____/ / /_/ |  |  /  |_| |  |_|  \  \___ / __ \|  | \   ___/ \___ \  ')
    print('/____  ||   __/ \____/|__| |__||__|  / ____|         \____ |____/|   __/|____/__|\___  |____  /__|  \___  \____  | ')
    print('     \/ |__|                         \/                   \/     |__|                \/     \/          \/     \/  ')
    
    # Parse program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='spotify user id')
    parser.add_argument('-l', '--list', action='store_true', help='list all duplicates')
    args = parser.parse_args()
    if args.user:
        user = args.user
    else:
        print("Whoops, need your user id!")
        print(parser.print_help())
        sys.exit()

    # Authorization scope:
    # https://developer.spotify.com/documentation/general/guides/scopes/#playlist-modify-public
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(user,
                    scope=scope,
                    client_id=os.getenv('SPOTIFY_ID'),
                    client_secret=os.getenv('SPOTIFY_SECRET'),
                    redirect_uri=os.getenv('SPOTIFY_REDIRECT'))

    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(user)
        
        # Finding duplicates by song names, n tracks their position and act as dictionary key
        n = 0
        names = []
        music = {}
        print("\nYour playlists:\n")

        # Get spotify data for user
        for playlist in playlists['items']:
            
            if playlist['owner']['id'] == user:
                
                print(playlist['name'], 'Total tracks:', playlist['tracks']['total'])

                playlist_id = playlist['id']
                results = sp.playlist(playlist_id, fields="tracks,next")
                tracks = results['tracks']

                for i, item in enumerate(tracks['items']):
                    track = item['track']
                    artists = ', '.join([track['artists'][x]['name'] for x in range(len(track['artists']))])
                    album = track['album']['name']
                    music[n] = {'playlist': playlist['name'], 
                                'album': album, 
                                'artists': artists, 
                                'playlist_id': playlist_id,
                                'uri': track['uri'].split(":")[2],
                                'position': i}
                    names.append(track['name'])
                    n = n + 1

        names = [x for x in names if x is not None]
        
        print("\nYour duplicates:")
        
        if args.list:
            # List duplicates
            print(f"\n{'Song':40s}{'playlist':40s}{'album':40s}{'artists':40s}position")
            for name, dup in sorted(list_duplicates(names)):               
                for n in dup:
                    print(f"{name:40s}{music[n]['playlist']:40s}{music[n]['album']:40s}{music[n]['artists']:40s}{music[n]['position']}")
        else:
            # List songs and take user input which to remove
            for name, dup in sorted(list_duplicates(names)):
                print(f"\n--- song: {name} ---")
                print(f"{'#':5s}{'playlist':40s}{'album':40s}{'artists':40s}position")
                options = "Stop: q, Skip: 0, Remove from:"
                for i, n in enumerate(dup):
                    print(f"{str(i+1):5s}{music[n]['playlist']:40s}{music[n]['album']:40s}{music[n]['artists']:40s}{music[n]['position']}")
                    options += f" {i+1} - {music[n]['playlist']},"
                choice = input(f"\n{options.strip(',')}\n")
                
                # Create track object to be removed
                to_be_removed = []
                try:
                    choice = int(choice)
                    if choice == 0: 
                        print("Skip!")
                        continue
                    else:
                        if choice in range(1, len(dup) + 1):
                            to_be_removed = [{'playlist_id': music[dup[choice-1]]['playlist_id'], 
                                              'tracks': [{'uri': music[dup[choice-1]]['uri'], 'positions': [music[dup[choice-1]]['position']]}]}]
                        if not to_be_removed:
                            print("No matching digit, jumping to next song ...")
                            continue
                        print(to_be_removed)
                except ValueError:
                    choices = choice.split()
                    try:
                        choices = [int(choice) for choice in choices]
                        for choice in choices:
                            if choice in range(1, len(dup) + 1):
                                to_be_removed.append({'playlist_id': music[dup[choice-1]]['playlist_id'], 
                                                      'tracks': [{'uri': music[dup[choice-1]]['uri'], 'positions': [music[dup[choice-1]]['position']]}]})
                        if not to_be_removed:
                            print("No matching digits, jumping to next song ...")
                            continue
                    except ValueError:
                        if 'q' in choice:
                            print('Stopping ...')
                            break
                        print("Input is not an integer or multiple space separated integers, jumping to next song ...")
                        continue
                
                # Perform the actual removal
                for track in to_be_removed:
                    try:
                        sp.user_playlist_remove_specific_occurrences_of_tracks(user, track['playlist_id'], track['tracks'])
                    except:
                        print('Error removing, jumping to next song ...')
    else:
        print("Can't get token for", user)
