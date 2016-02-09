#!/usr/bin/python

import sys
import spotipy
import spotipy.util as util
import random

class SPG:

    def __init__(self, username, token=None, playlistName="Random Mix", tracksCount=30):
        self.scope = ' '.join(['user-library-read', 'playlist-modify-public', 'playlist-modify-private'])
        self.username = username
        self.playlistName = playlistName
        self.tracksCount = tracksCount

        self.token = token
        self.token = util.prompt_for_user_token(self.username, self.scope)

        self.sp = None

        if self.token:
            self.sp = spotipy.Spotify(auth=self.token)
        else:
            print("Can't get token for", username)
            sys.exit(1)

    def getPlaylist(self):
        print "Searching playlist %s..." % (self.playlistName)
        limit = 50
        offset = 0
        while True:
            playlists = self.sp.user_playlists(self.username, limit=limit, offset=offset)
            if len(playlists["items"]) == 0:
                break
            offset += limit
            for playlist in playlists['items']:
                if playlist['name'] == self.playlistName:
                    self.playlistUri = playlist["uri"]
                    return

        # not found, create playlist
        res = self.sp.user_playlist_create(self.username, self.playlistName)
        self.playlistUri = res["uri"]

    def getTracks(self):
        print "Reading tracks..."
        limit = 50
        offset = 0

        self.savedTracks = []
        print "Total: %s" % (len(self.savedTracks))

        while True:
            obj = self.sp.current_user_saved_tracks(limit=limit, offset=offset)

            if len(obj['items']) == 0:
                break

            offset += limit
            for item in obj['items']:
                self.savedTracks.append(item['track'])

            print "Total: %s" % (len(self.savedTracks))


    def cleanPlaylist(self):
        print "Cleaning playlist %s..." % (self.playlistName)

        limit = 50
        offset = 0

        while True:
            tracks = self.sp.user_playlist_tracks(self.username, self.playlistUri, limit=limit, offset=offset)

            if len(tracks['items']) == 0:
                break

            offset += limit

            tracksIds = []
            for track in tracks['items']:
                tracksIds.append(track['track']['uri'])

            self.sp.user_playlist_remove_all_occurrences_of_tracks(self.username, self.playlistUri, tracksIds)


    def run(self):
        self.getPlaylist()

        self.getTracks()

        self.cleanPlaylist()

        sampledTracks = random.sample(self.savedTracks, self.tracksCount)

        tracksIds = []
        for track in sampledTracks:
            tracksIds.append(track['uri'])

        self.sp.user_playlist_add_tracks(self.username, self.playlistUri, tracksIds)

if __name__=="__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username [playlistName] [tracksCount]" % (sys.argv[0],))
        sys.exit()

    playlistName = "Random Mix"
    if len(sys.argv) > 2:
        playlistName = sys.argv[2]

    tracksCount = 30
    if len(sys.argv) > 3:
        tracksCount = sys.argv[3]

    app = SPG(username, playlistName=playlistName, tracksCount=tracksCount)
    app.run()
