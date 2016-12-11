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

    def play(self):
        self._process = subprocess.Popen(
                ["omxplayer", self._path, "--amp", str(self._vol*300), "--no-osd"],
                stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        self._set_status(Song.Status.PLAYING)

    def pause(self):
        self._send("p")

    def stop(self, fin=True):
        self._send("q")

    def next(self):
        self.stop(False)
        self._index += 1
        if len(self.songs) <= self._index:
            self._fin = True
            raise EOS("End of List")
        self.play_this()

    def prev(self):
        self.stop(False)
        self._index -= 1
        self.play_this()

    def random(self):
        random.shuffle(self._song_list)

    def lineal(self):
        self._song_list = self.songs.copy()

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


class Player():
    pass

   

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
