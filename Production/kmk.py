import board
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.display import Display, TextEntry, ImageEntry
from kmk.extensions.display.ssd1306 import SSD1306

# Initialize keyboard
keyboard = KMKKeyboard()

# Pin configuration for Seeed Studio XIAO RP2040
keyboard.col_pins = (board.D0, board.D1, board.D2, board.D3)  # 4 keys
keyboard.row_pins = (board.D6,)  # Single row for 4 keys
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# Initialize extensions
media_keys = MediaKeys()
keyboard.extensions.append(media_keys)

# Encoder configuration
encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)

# Encoder 1: Volume (pins D7 and D8)
encoder_handler.pins = (
    (board.D7, board.D8, None, False),  # Volume encoder (CLK, DT, SW, inverted)
    (board.D9, board.D10, None, False),  # Brightness encoder (CLK, DT, SW, inverted)
)

# Encoder map
encoder_handler.map = [
    ((KC.VOLU, KC.VOLD, None),),  # Volume up/down
    ((KC.BRIGHTNESS_UP, KC.BRIGHTNESS_DOWN, None),),  # Brightness up/down
]

# OLED Display configuration (I2C on pins D4=SDA, D5=SCL)
i2c = board.I2C()
driver = SSD1306(
    i2c=i2c,
    device_address=0x3C,
)

display = Display(
    display=driver,
    width=128,
    height=64,
    brightness=1.0,
    flip=False,
)

# Custom display entries for volume and brightness
class VolumeEntry(TextEntry):
    def __init__(self):
        super().__init__(text="Vol: 50%", x=0, y=0, x_anchor="L", y_anchor="T")
        self.volume_level = 50
    
    def update(self, keyboard):
        # Update volume display (simulated percentage)
        self.text = f"Vol: {self.volume_level}%"
        return True

class BrightnessEntry(TextEntry):
    def __init__(self):
        super().__init__(text="Bri: 50%", x=0, y=20, x_anchor="L", y_anchor="T")
        self.brightness_level = 50
    
    def update(self, keyboard):
        # Update brightness display (simulated percentage)
        self.text = f"Bri: {self.brightness_level}%"
        return True

class TitleEntry(TextEntry):
    def __init__(self):
        super().__init__(text="HackPad v1.0", x=64, y=50, x_anchor="M", y_anchor="B")

# Add display entries
volume_display = VolumeEntry()
brightness_display = BrightnessEntry()
title_display = TitleEntry()

display.entries = [volume_display, brightness_display, title_display]

keyboard.extensions.append(display)

# Keymap - 4 keys in a single row
keyboard.keymap = [
    [KC.A, KC.B, KC.C, KC.D]  # Replace with your desired keys
]

# Custom encoder callbacks to update display
original_encoder_handler_on_runtime_enable = encoder_handler.on_runtime_enable

def custom_on_runtime_enable(keyboard):
    original_encoder_handler_on_runtime_enable(keyboard)
    
    # Store original encoder callback
    original_callback = encoder_handler._on_encoder
    
    def custom_encoder_callback(state):
        # Call original callback
        original_callback(state)
        
        # Update display values based on encoder state
        if state.index == 0:  # Volume encoder
            if state.direction == 1:  # Clockwise
                volume_display.volume_level = min(100, volume_display.volume_level + 5)
            else:  # Counter-clockwise
                volume_display.volume_level = max(0, volume_display.volume_level - 5)
        
        elif state.index == 1:  # Brightness encoder
            if state.direction == 1:  # Clockwise
                brightness_display.brightness_level = min(100, brightness_display.brightness_level + 5)
            else:  # Counter-clockwise
                brightness_display.brightness_level = max(0, brightness_display.brightness_level - 5)
    
    encoder_handler._on_encoder = custom_encoder_callback

encoder_handler.on_runtime_enable = custom_on_runtime_enable

if __name__ == '__main__':
    keyboard.go()