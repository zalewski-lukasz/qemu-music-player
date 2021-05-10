#!/usr/bin/python
import gpiod
import pygame
import time
import glob
import os
import curses

music_directory = 'songs'
volume_step = 0.125
control_with_gpio = True 

class Song:

    def __init__(self, name):
        self.name = name
        self.picked = False

    def __str__(self):
        return f"->\t{self.name}" if self.picked == True else f"*\t{self.name}"

class Playlist:

    def __init__(self, files):
        self.index_of_picked = 0
        self.paused = False
        self.songs = list()
        self.volume = 0.5
        self.is_playing = False
        self.leds_number = 4
        pygame.mixer.music.set_volume(0.5)
        for file in files:
            song = Song(file)
            if len(self.songs) == 0:
                song.picked = True
            self.songs.append(song)
        self.picked_song_name = ""
        if len(self.songs) > 0:
            self.picked_song_name = self.songs[self.index_of_picked].name

    def print(self, stdscr):

        if stdscr is not None:
            curses.curs_set(0)
        else:
            clear_console()

        if len(self.songs) == 0:
            if stdscr is None:
                print("PLAYLIST IS EMPTY")
            else:
                stdscr.addstr(0, 0, "PLAYLIST IS EMPTY")
            return

        pos = 0
        if stdscr is not None:
            stdscr.addstr(pos, 0, "PLAYLIST:")
        else:
            print("PLAYLIST:\n")
        pos += 2
        for song in self.songs:
            if stdscr is not None:
                stdscr.addstr(pos, 1, str(song))
            else:
                print(song)
            pos += 1

        pos += 1  
        if stdscr is not None:
            stdscr.addstr(pos, 0, f"VOLUME: {self.volume}")
        else:
            print(f"\nVOLUME: {self.volume}")

        if stdscr is not None:
            stdscr.refresh()

    def pick_next(self):
        self.songs[self.index_of_picked].picked = False
        self.index_of_picked += 1
        if self.index_of_picked >= len(self.songs):
            self.index_of_picked = 0
        self.songs[self.index_of_picked].picked = True

    def pick_previous(self):
        self.songs[self.index_of_picked].picked = False
        self.index_of_picked -= 1
        if self.index_of_picked < 0:
            self.index_of_picked = len(self.songs) - 1
        self.songs[self.index_of_picked].picked = True

    def play_picked(self):
        for song in self.songs:
            if song.picked == True and self.is_playing == False:
                self.is_playing = True
                play_music(song.name)
                return
            if song.picked == True and self.is_playing == True:
                self.is_playing = False
                play_music(song.name)
                return

    def play_next(self, stdscr):
        stop_music()
        self.pick_next()
        self.play_picked()
        self.print(stdscr)

    def play_previous(self, stdscr):
        stop_music()
        self.pick_previous()
        self.play_picked()
        self.print(stdscr)

    def increase_volume(self, stdscr):
        if self.volume < 1:
            self.volume += volume_step
            self.leds_number += 1
        pygame.mixer.music.set_volume(self.volume)
        self.print(stdscr)

    def decrease_volume(self, stdscr):
        if self.volume > 0:
            self.volume -= volume_step
            self.leds_number -= 1
        pygame.mixer.music.set_volume(self.volume)
        self.print(stdscr)
        
    def pause(self, stdscr):
        pygame.mixer.music.pause()
        self.print(stdscr)

    def unpause(self, stdscr):
        pygame.mixer.music.unpause()
        self.print(stdscr)
    
    def resume_playing(self, stdscr):
        if self.paused == True:
            self.paused = False
            self.unpause(stdscr)
        else:
            self.paused = True
            self.pause(stdscr)
        
def prepare_chip():
    return gpiod.Chip('9008000.gpio')

def prepare_leds(chip):
    leds = list()
    for i in range (24, 32):
        led = chip.get_line(i)
        led.request(consumer="its_me", type=gpiod.LINE_REQ_DIR_OUT)
        leds.append(led)
    return leds

def prepare_switch(chip):
    switch = chip.get_line(0)
    switch.request(consumer="its_me", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
    return switch

def prepare_buttons(chip):
    buttons = list()
    for i in range(12, 18):
        button = chip.get_line(i)
        button.request(consumer="its_me", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        buttons.append(button)
    return buttons

def turn_led_on(led):
    led.set_value(1)

def turn_off_led(led):
    led.set_value(0)

def adjust_leds(leds, leds_number):
    for i in range(0, 8):
        if i < leds_number:
            turn_led_on(leds[i])
        else:
            turn_off_led(leds[i])


def play_music(song_name):
    pygame.mixer.music.load(song_name)
    pygame.mixer.music.play()

def stop_music():
    pygame.mixer.music.stop()

def init_player():
    pygame.mixer.init()

def get_music_files():
    files = []
    for file in glob.glob(f"{music_directory}/*.wav"):
        files.append(file)
    return files

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def run():
    
    init_player()
    pygame.init()

    chip = prepare_chip()
    leds = prepare_leds(chip)
    switch = prepare_switch(chip)
    buttons = prepare_buttons(chip)

    stdscr = None

    files = get_music_files()
    playlist = Playlist(files)

    playlist.print(stdscr)
    adjust_leds(leds, playlist.leds_number)
    while True:

        if control_with_gpio == True:
            for i in range (0, 6):
                btn = buttons[i]
                ev_line = btn.event_wait(1)
                if ev_line:
                    event = btn.event_read()
                    if event.type == gpiod.LineEvent.FALLING_EDGE: continue
                    if i == 0: playlist.play_previous(stdscr)
                    if i == 1: playlist.play_picked()
                    if i == 2: playlist.resume_playing(stdscr)
                    if i == 3: playlist.play_next(stdscr)
                    if i == 4: 
                        playlist.decrease_volume(stdscr)
                        adjust_leds(leds, playlist.leds_number)
                    if i == 5: 
                        playlist.increase_volume(stdscr)
                        adjust_leds(leds, playlist.leds_number)



def main(stdscr):
     
    init_player()
    pygame.init()

    files = get_music_files()
    playlist = Playlist(files)
    
    playlist.print(stdscr)

    while True:

        if control_with_gpio == False:
            stdscr.nodelay(1)
            key = stdscr.getch()
            
            if key == curses.KEY_DOWN:
                playlist.play_next(stdscr)
            if key == curses.KEY_UP:
                playlist.play_previous(stdscr)
            if key == curses.KEY_RIGHT:
                playlist.increase_volume(stdscr)
            if key == curses.KEY_LEFT:
                playlist.decrease_volume(stdscr)
            if key == curses.KEY_PPAGE:
                playlist.resume_playing(stdscr)
            if key == curses.KEY_NPAGE:
                playlist.play_picked()
                playlist.print(stdscr)
            if key == ' ':
                pass

if __name__ == "__main__":
    if control_with_gpio:
        run()
    else:
        curses.wrapper(main)