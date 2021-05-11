# qemu-music-player
Project implementing simple music player and file server for qemu system

## Information
The goal of the application is to try to create and use music player in emulated system simulating embedded system environment, close in behaviour to Raspberry Pi devices. As a result, simple application in Python was created to make use of the GUI emulator and its buttons and LED diodes. It gives user the possibility to:
- play the picked song
- pause/unpause the song
- pick next song
- pick previous song
- increase/decrease the volume

There is also an option to manage the song playlist with the web interface, which was created thanks to the Flask framework. It gives the following options:
- delete the chosen song 
- download the chosen song onto the host system
- upload the song from the host system

For now, the application has also support for the keyboard with usage of the curses module, if a certain flag is set in code as False. It is mostly here only to provide the ability to test the system without the GUI setup, and with the standard keyboard system.

## Usage
To make use of the system, the user first needs to compile the whole buildroot directory. It can be accomplished with the command
```
./build.sh
```
After that, in other terminal the GUI must be turned on. It can be accomplished by typing
```
./run_before
```
After succesfull compilation, the user can use the system after running the command
```
./runme
```
There are two scripts provided by the system, which can be run by the user at any point after logging in as a root. 
```
RunMusicPlayer
```
The above command runs the player. To run the program, the application was provided with the following actions on the button presses:
- 12 to pick the previous song
- 13 to play the picked song
- 14 to pause/unpause the song
- 15 to pick the next song
- 16 to decrease the volume
- 17 to increase the volume

The levels of the volume are symbolized by the LED diodes and by the console UI. Picked song is also shown there

```
RunMusicServer
```
The above command runs the server. To access it, on the host system in browser the following address must be typed in
```
localhost:8888
```
After that, the user will be able to choose files for deletion, upload and download the file. Only .wav files are used.
