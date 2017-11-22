### rpi-rotary-encoder-and-button-lib

# Raspberry Pi interface panel object
Python library to make a simple and effective interface for a control panel built with push buttons and rotary encoders. Designed for the Raspberry Pi and uses pigpio daemon.

# Generic setup
Its easy to get going
- Create an InterfacePanel object
- Add buttons and rotary encoders using ``add_button`` and ``add_rotary_encoder`` methods
- Sit back and relax, when a user interacts you will get a callback

See example.py

# Powerfull with features

- Uses interrupts to listen to gpio's
- Listen to only push-downs or also duration (dual callback)
- Dual resolution counting of rotary encoder (counts on rising and falling edge of both outputs)
- Configurable for ground->io or 5v->io buttons and encoders
- Configurable for normally open (NC) or normally closed (NC) buttons
- Uses built in pull-ups and pull-downs in Raspberry Pi

# How to connect
Connect the switch between ground and a io. This is the default way, using ``io_gnd = True`` and ``normally_closed`` assuming your switch opens on click.

--------+
        |
        |
R       |-+
A   I/0 | |------+
S       |-+      |
P       |        |
B       |        o
E       |         \
R       |        --\---| Switch
R       |           \
Y       |        o   \
        |-+      |
P   GND | |------+
I       |-+
        |
        |
--------+
