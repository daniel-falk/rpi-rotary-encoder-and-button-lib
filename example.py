from InterfacePanel import InterfacePanel
from time import sleep

# Specify IO pins

rotary_encoder = (6, 13)

buttons = {
        "back" : 19,
        "pause" : 5,
        "forward" : 16,
        "meny" : 12,
        "ok" : 20}


def button_up(name, duration):
    print("Duration for '{}' was {} seconds".format(name, duration))


def button_callback(name):
    if name in ["back", "forward"]:
        print("Button '{}' down....".format(name))
        return button_up
    else:
        print("Button '{}' pressed.".format(name))
        return None


def rotation_callback(pos, dir):
    dir = "<--" if dir < 0 else "-->"
    print("{} Pos: {}".format(dir, pos))


with InterfacePanel() as panel:
    panel.add_rotary_encoder("Wheel", rotation_callback, *rotary_encoder)
    for name, pin in buttons.iteritems():
        panel.add_button(name, button_callback, pin)

    sleep(60)


print("Times up! Exiting...")
