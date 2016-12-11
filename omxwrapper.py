#!/usr/bin/python3

import os
import random
import subprocess
from enum import Enum
from zashel.utils import daemonize

class EOS(Exception):
    pass

class Song():
    class Status(Enum):
        STOPPED = 0
        PLAYING = 1
        PAUSED = 2

    def __init__(self, path, vol=int()):
        self._path = path
        self._process = None
        self._vol = vol
        self._status = Song.Status.STOPPED

    def __del__(self):
        self.stop()

    @property
    def is_playing(self):
        if self._process is not None:
            return self._process is not None
        return False

    @property
    def path(self):
        return self._path

    @property
    def status(self):
        return self._status

    def play(self, pos):
        self._process = subprocess.Popen(
                ["omxplayer", self._path,
                    "--amp", str(self._vol*300),
                    "--no-osd",
                    "--pos", pos],
                stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        self._set_status(Song.Status.PLAYING)

    def pause(self):
        self._send("p")

    def next(self): #For CD compatibility
        self.stop()

    def prev(self):
        self.stop()

    def stop(self):
        self._send("q")

    def set_volume(self, vol):
        vol_now, self._vol = self._vol, vol
        while vol_now != vol:
            if vol_now < vol:
                self._send("+")
                vol_now += 1
            elif vol_now > vol:
                self._send("-")
                vol_now -= 1

    def vol_up(self):
        self.set_volume(self._vol+1)

    def vol_down(self):
        self.set_volume(self._vol-1)

    def _send(self, text):
        if self.is_playing is True:
            try:
                self._process.stdin.write(bytearray(text, "utf-8"))
                self._process.stdin.flush()
            except KeyboardInterrupt:
                raise
            except:
                pass

    def _set_status(self, status):
        assert isinstance(status, Song.Status)
        self._status = status

class CD(Song):
    pass #TODO


class Player():
    def __init__(self, paths=None):
        if paths is None:
            self._paths = list()
            self.include_path(os.path.normpath("~/Music"))
        else:
            self._paths = paths
        self.update_songs()

    def include_path(self, path):
        self._paths.append(path)
        self.update_songs()

    def remove_path(self, path):
        if path in self._paths:
            self._paths.remove(path)
        self.update_songs()

    def update_songs(self):
        def songify(song):
            if song.split(".")[-1] == "mp3":
                return Song(song)
            elif song.split(".")[-1] in ("flac", "iso"):
                return CD(song)

        self._songs = [
            [songify(song) for song in os.listdir(path)]
            for path in self._paths
            ]
   

if __name__ == "__main__":
    play = Player()
    play.random()
    print(play.songs)
    play.loop()
    while True:
        act_in = input("Action: ")         
        if act_in in ("next", "prev", "pause", "vol_up", "vol_down"):
            play.__getattribute__(act_in)()
        elif act_in == "stop":
            play.stop(True)
        if play._fin == True:
            break
