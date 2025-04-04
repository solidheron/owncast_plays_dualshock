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


## Known Issues
- script has randomly inputted the last 15 chatroom responses during the fix for that happens to make it so if 15 or more inputs in between cycles then there wont be any button presses

## Contributing
Pull requests and feature suggestions are welcome! Please open an issue if you encounter any bugs or have ideas for improvements.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---
**Author:** [solidheron](https://github.com/solidheron)

