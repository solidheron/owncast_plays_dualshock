import vgamepad as vg
import time
import re
import unicodedata
import threading
import hashlib
import asyncio
from typing import Dict, Union, List
from playwright.async_api import async_playwright, TimeoutError
import os

chatroom_url = "https://live.24hrkpop.com/embed/chat/readwrite/"
stop_event = threading.Event()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class DS4Tester:
    def __init__(self):
        self.gamepad = vg.VDS4Gamepad()
        self._initialize_mappings()
        self.ps_button_thread = threading.Thread(target=self._press_ps_periodically, daemon=True)
        self.ps_button_thread.start()

    def _press_ps_periodically(self):
        """Presses the PS button every 30 minutes. for save states"""
        while True:
            time.sleep(1800)  # Wait for 30 minutes
            #print("Pressing PS button to prevent idle timeout.")
            self._handle_special_button("ps")

    def _initialize_mappings(self):
        """Initialize all controller mappings"""
        self.button_mapping = {
            "square": vg.DS4_BUTTONS.DS4_BUTTON_SQUARE,
            "s": vg.DS4_BUTTONS.DS4_BUTTON_SQUARE,
            "triangle": vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
            "t": vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
            "v": vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
            "circle": vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
            "o": vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
            "cross": vg.DS4_BUTTONS.DS4_BUTTON_CROSS,
            "x": vg.DS4_BUTTONS.DS4_BUTTON_CROSS,
            "l1": vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT,
            "r1": vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
            "l2": vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_LEFT,
            "r2": vg.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT,
            "l3": vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT,
            "r3": vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT,
            "select": vg.DS4_BUTTONS.DS4_BUTTON_SHARE,
            "start": vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS,
            "share": vg.DS4_BUTTONS.DS4_BUTTON_SHARE,
            "options": vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS
        }

        self.special_button_mapping = {
            "ps": vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS,
            "touchpad": vg.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_TOUCHPAD
        }

        self.dpad_mapping = {
            "u": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
            "d": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
            "l": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
            "r": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
            "up": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
            "down": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
            "left": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
            "right": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
            # Diagonals
            "ul": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHWEST,
            "ur": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHEAST,
            "dl": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHWEST,
            "dr": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHEAST,
            "lu": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHWEST,
            "ru": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHEAST,
            "ld": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHWEST,
            "rd": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHEAST,
        }

    def _combine_dpad_directions(self, directions: List[int]) -> int:
        """
        Combine multiple D-pad directions into a single state.
        """
        if len(directions) == 1:
            return directions[0]

        # Define diagonal combinations
        if vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH in directions and vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST in directions:
            return vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHEAST
        if vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH in directions and vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST in directions:
            return vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHWEST
        if vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH in directions and vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST in directions:
            return vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHEAST
        if vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH in directions and vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST in directions:
            return vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHWEST

        # If no valid combination, default to the first direction
        return directions[0]

    def reset_all(self):
        """Turn off all button presses and reset the gamepad state."""
        # Release all regular buttons
        for button in self.button_mapping.values():
            self.gamepad.release_button(button)
        # Release special buttons
        for special in self.special_button_mapping.values():
            self.gamepad.release_special_button(special)
        # Reset the D-pad to neutral
        self.gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
        self.gamepad.update()
        #print("All button presses have been turned off.")

    def press_input(self, input_name: Union[str, List[str]], duration: float = .2) -> None:
        """
        Press and release controller input(s).

        Args:
            input_name: Single input name as string or list of inputs for simultaneous press.
            duration: How long to hold the input(s) (in seconds).
        """
        if isinstance(input_name, list):
            self._press_multiple_inputs(input_name, duration)
        else:
            self._press_single_input(input_name, duration)

    def _press_single_input(self, input_name: str, duration: float) -> None:
        """Handle single input press."""
        input_name = input_name.lower()
        print(f"Attempting to press: {input_name}")

        if input_name in self.button_mapping:
            self._handle_button(input_name, duration)
        elif input_name in self.dpad_mapping:
            self._handle_dpad(input_name, duration)
        elif input_name in self.special_button_mapping:
            self._handle_special_button(input_name)
        else:
            print(f"Unrecognized input '{input_name}'. No button pressed.")
            self.reset_all()  # Turn off all button presses for invalid input

        time.sleep(0.04)  # Brief pause between inputs

    def _press_multiple_inputs(self, input_names: List[str], duration: float) -> None:
        """Handle simultaneous button presses more robustly."""
        #print(f"Pressing simultaneously: {', '.join(i.upper() for i in input_names)}")
        dpad_directions = []

        # Press buttons and collect D-pad directions
        for input_name in input_names:
            input_name = input_name.lower()
            if input_name in self.button_mapping:
                self.gamepad.press_button(self.button_mapping[input_name])
            elif input_name in self.dpad_mapping:
                dpad_directions.append(self.dpad_mapping[input_name])
            elif input_name in self.special_button_mapping:
                self.gamepad.press_special_button(self.special_button_mapping[input_name])
            else:
                # Invalid token: reset all buttons and raise error to be caught upstream.
                self.reset_all()
                raise ValueError(f"Invalid input: '{input_name}'")

        # If there are any D-pad inputs, combine and press them
        if dpad_directions:
            combined_direction = self._combine_dpad_directions(dpad_directions)
            self.gamepad.directional_pad(combined_direction)

        self.gamepad.update()
        time.sleep(duration)

        # Release buttons and reset D-pad
        for input_name in input_names:
            input_name = input_name.lower()
            if input_name in self.button_mapping:
                self.gamepad.release_button(self.button_mapping[input_name])
            elif input_name in self.dpad_mapping:
                self.gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
            elif input_name in self.special_button_mapping:
                self.gamepad.release_special_button(self.special_button_mapping[input_name])

        self.gamepad.update()
        time.sleep(0.04)  # Brief pause after release

    def _handle_button(self, button: str, duration: float) -> None:
        """Handle regular button press/release."""
        self.gamepad.press_button(self.button_mapping[button])
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(self.button_mapping[button])
        self.gamepad.update()

    def _handle_dpad(self, direction: str, duration: float) -> None:
        """Handle D-pad input."""
        self.gamepad.directional_pad(self.dpad_mapping[direction])
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
        self.gamepad.update()

    def _handle_special_button(self, button: str) -> None:
        """Handle special button press/release."""
        self.gamepad.press_special_button(self.special_button_mapping[button])
        self.gamepad.update()
        time.sleep(0.1)  # Shorter duration for special buttons
        self.gamepad.release_special_button(self.special_button_mapping[button])
        self.gamepad.update()

    def run_test_sequence(self, sequence: Union[List[str], List[List[str]]],
                          cycles: Union[int, None] = None) -> None:
        """
        Run through a test sequence which can include single or simultaneous inputs.

        Args:
            sequence: List of inputs (strings) or lists of inputs for simultaneous presses.
            cycles: Number of times to run the sequence (None for infinite).
        """
        print("Starting DS4 controller test...")
        time.sleep(2)  # Allow time for initialization

        try:
            count = 0
            while cycles is None or count < cycles:
                for item in sequence:
                    if isinstance(item, list):
                        # Simultaneous press
                        self.press_input(item)
                    else:
                        # Single press
                        self.press_input(item)
                print("\n--- Completed test cycle ---\n")
                count += 1

        except KeyboardInterrupt:
            print("\nTest sequence terminated by user")


def remove_overlap(previous_cycle, this_cycle):
    """
    Removes the overlapping part of this_cycle with previous_cycle.
    
    :param previous_cycle: List of messages from the previous cycle.
    :param this_cycle: List of messages from the current cycle.
    :return: A version of this_cycle with the overlapping part removed.
    """
    max_overlap = min(len(previous_cycle), len(this_cycle))  # Limit overlap check

    max_overlap = min(len(previous_cycle), len(this_cycle))  
    for i in range(max_overlap, 0, -1):  
        if previous_cycle[-i:] == this_cycle[:i]:  
            return this_cycle[i:]  
    return this_cycle  



async def get_entire_chat(page):
    """Fetch the entire chat history and return as a list of (username, message)."""
    chat_data = []
    try:
        messages = await page.query_selector_all(".ChatUserMessage_messagePadding__f7kp4")
        for msg in messages:
            username_element = await msg.query_selector(".ChatUserMessage_user__u7aBR")
            content_element = await msg.query_selector(".ChatUserMessage_message__JJiP9")
            
            username = await username_element.inner_text() if username_element else "Unknown"
            content = await content_element.inner_text() if content_element else "(No Content)"
            
            chat_data.append((username, content))
    except Exception as e:
        print(f"Error fetching entire chat: {e}")
    
    return chat_data

async def get_last_10_messages_from_chat(page):
    """Fetch the last 10 chat messages and return as a list of (username, message)."""
    chat_data = []
    try:
        messages = await page.query_selector_all(".ChatUserMessage_messagePadding__f7kp4")
        last_messages = messages[-10:]  # Get the last 10 messages
        for msg in last_messages:
            username_element = await msg.query_selector(".ChatUserMessage_user__u7aBR")
            content_element = await msg.query_selector(".ChatUserMessage_message__JJiP9")
            
            username = await username_element.inner_text() if username_element else "Unknown"
            content = await content_element.inner_text() if content_element else "(No Content)"
            
            chat_data.append((username, content))
    except Exception as e:
        print(f"Error fetching last 10 messages: {e}")
    
    return chat_data

async def monitor_chat(page):
    """Continuously check for new chat messages, avoiding duplicates."""
    seen_messages = set()
    try:
        while True:
            messages = await get_entire_chat(page)
            for username, content in messages:
                message_id = f"{username}: {content}"  # Unique message identifier
                if message_id not in seen_messages:
                    seen_messages.add(message_id)
                    print(username, content)
            await asyncio.sleep(5)  # Adjust timing based on chat activity
    except Exception as e:
        print(f"Error in chat monitoring: {e}")

async def check_chat_messages(page, stop_event, ds4_tester):
    """Check chat messages at regular intervals."""
    #last_username, last_timestamp, last_content = None, None, None
    username_map = {}
    #previous_last_5_message_content = await get_last_5_messages_from_chat(page)  # gets the last 5 messages
    previous_cycle_last_10_messages_from_chat = await get_last_10_messages_from_chat(page)
    counter = 10

    #Already_executed_commands = previous_cycle_last_10_messages_from_chat
    while not stop_event.is_set():
        try:
            #last_5_message_content = await get_last_5_messages_from_chat(page)            
            this_cycle_last_10_messages_from_chat = await get_last_10_messages_from_chat(page)
            
            if counter == 10 and this_cycle_last_10_messages_from_chat == previous_cycle_last_10_messages_from_chat: #extract_messages_regex(this_cycle_last_10_messages_from_chat) == extract_messages_regex(previous_cycle_last_10_messages_from_chat):
                await asyncio.sleep(2)
                continue
            if counter == 10:
                counter = 0
            counter = counter + 1
            
            Commands_to_execute_raw = remove_overlap(previous_cycle_last_10_messages_from_chat, this_cycle_last_10_messages_from_chat)
            previous_cycle_last_10_messages_from_chat = this_cycle_last_10_messages_from_chat
            
            if len(Commands_to_execute_raw) == 15:
                print('remove_overlap glitch implimenting failsafe')
                Commands_to_execute_raw = Commands_to_execute_raw[-1]
            
            #previous_cycle_last_10_messages_from_chat = this_cycle_last_10_messages_from_chat
            for raw_command in Commands_to_execute_raw:

                if isinstance(raw_command, tuple) and len(raw_command) == 2:
                    Username, raw_extract = raw_command
                    # Process Username and raw_extract as needed
                else:
                    print(f"Invalid command format: {raw_command}")
                Commands_to_execute_raw1 = [raw_extract]


                #print(f"Commands_to_execute_raw:{Commands_to_execute_raw1}")
                Commands_to_execute_messages = Commands_to_execute_raw1 #extract_messages_regex(Commands_to_execute_raw1)
                #print(f"Commands_to_execute_messages:{Commands_to_execute_messages}")
                Commands_to_execute_Username = Username #extract_sender(Commands_to_execute_raw1)                    
                if isinstance(Commands_to_execute_messages, list):
                    tokens = " ".join(Commands_to_execute_messages).split()
                else:
                    tokens = Commands_to_execute_messages.split() if Commands_to_execute_messages else []

                base_command = tokens[0] if tokens else ""
                repetitions = 1
                if len(tokens) > 1 and tokens[-1].isdigit():
                    repetitions = int(tokens[-1])
                    tokens.pop()
                    if repetitions > 15:
                        repetitions = 15
                # Use tokens up to the word "Copy" if present.
                if "Copy" in tokens:
                    message_tokens = tokens[:tokens.index('Copy')]
                else:
                    message_tokens = tokens
                #print(f"message_tokens:{message_tokens}")
                base_command = base_command.lower()

                if Commands_to_execute_Username:
                    print(f"Username: {Commands_to_execute_Username}")
                #if this_cycles_lst_5_time_stamps:
                #    print(f"Timestamp: {this_cycles_lst_5_time_stamps[-1]}")
                if repetitions == 1:
                    print(f"Executing {message_tokens[0]}")
                else:
                    print(f"Executing {message_tokens[0]} {repetitions} time")
                # Wrap press_input in a try/except to handle invalid token errors.
                try:
                    ds4_tester.press_input(message_tokens)
                    for i in range(repetitions-1):
                        ds4_tester.press_input(message_tokens)
                    print("---")
                except ValueError as ve:
                    #print(f"Invalid command encountered: {ve}. Turning off all button presses.")
                    ds4_tester.reset_all()
            
            
        except Exception as e:
            print(f"Error processing message: {e}")
            await page.reload()
            print("Page refreshed.")
                
        #await asyncio.sleep(1)

async def run_asyncio_tasks(ds4_tester):
    """Run the async tasks with Playwright."""
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.firefox.launch(headless=True)
            print("Firefox browser launched.")
            page = await browser.new_page()
            await page.goto(chatroom_url, timeout=15000)
            print("Page loaded.")
            
            await page.wait_for_selector(".ChatUserMessage_messagePadding__f7kp4", state="attached", timeout=15000)
            print("Chat messages detected.")
            chat_task = asyncio.create_task(check_chat_messages(page, stop_event, ds4_tester))
            await chat_task
            
            # Fetch entire chat history initially
            #chat_history = await get_entire_chat(page)
            #print("Full chat history:", chat_history)

            await page.reload()
            print("Page refreshed.")
                        
            # Start monitoring chat
            #await monitor_chat(page)

        except TimeoutError:
            print("Error: Timed out while waiting for the page or message.")
        except Exception as e:
            print(f"Error during Playwright execution: {e}")
        finally:
            if browser:
                print("Closing browser...")
                await browser.close()

def main():
    tester = DS4Tester()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stop_event = threading.Event()
    loop.run_until_complete(run_asyncio_tasks(tester))

if __name__ == "__main__":
    main()
