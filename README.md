# Owncast Plays DualShock

This repository contains a script that enables users to control a DualShock-compatible game using chat commands in an Owncast livestream. Inspired by "Twitch Plays" style interactions, this setup allows viewers to send commands through chat, which are then translated into game inputs.

## Features

- Parses chat messages from an Owncast server.
- Maps chat commands to DualShock controller inputs.

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/solidheron/owncast_plays_dualshock.git
   cd owncast_plays_dualshock
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your Owncast chat endpoint and game input mappings in `config.py`.

## Usage

Run the script with:
```sh
python owncast_plays.py
```
this script was built around duckstation emulator make sure to run the script first then hook it up to (duckstation) emulator

### Chat Command Format
Viewers can send commands in chat using predefined keywords. Example:
```
up    # Move up
down  # Move down
x     # Press X button
start # Start button
t     # press triangle
ur    # press up and right simultaneously 
```
add numbers to the end commands to repeat the command up to 15 times
```
up 5          # Move up 5 times
down right 10 # Move down 10 times
x 3           # Press X button times
r1 1          # press right 1 shoulder button 1 time
t s 4          # press triangle and square 4 times
dl 2           # press down and left simultaneously 2 times
```


## Known Issues
- script has randomly inputted the last 15 chatroom responses during the fix for that happens to make it so if 15 or more inputs in between cycles then there wont be any button presses

## Contributing
Pull requests and feature suggestions are welcome! Keep in mind i dont have owncast server so I might not be able to test or figure out any improvements

## License
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES, OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE,
ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to https://unlicense.org

---
**Author:** [solidheron](https://github.com/solidheron)

