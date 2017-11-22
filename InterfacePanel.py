import pigpio

from RotaryEncoder import RotaryEncoder

class InterfacePanel:

    class Button:
        def __init__(self, name, pin, callback, debounce, rest_level, iocb):
            self.name = name
            self.pin = pin
            self.cb = callback
            self.debounce = debounce
            self.rest_level = rest_level
            self.t_last_rising = 0
            self.t_down = 0
            self.release_cb = None
            self.iocb = iocb

    class Encoder:
        def __init__(self, rotary_encoder, name):
            self.rot_enc = rotary_encoder
            self.name = name

    '''
    InterfacePanel constructor...

    If no gpio (pigpio pi object) is supplied a new connection to the local daemon is started.
    '''
    def __init__(self, gpio=None):
        self.gpio = gpio if gpio else pigpio.pi()
        self.cbs = [];
        self.rot_enc = dict()
        self.buttons = dict()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for r in self.rot_enc.values():
            r.rot_enc.close()

        for b in self.buttons.values():
            b.iocb.cancel()

        self.gpio.stop()

    def close(self):
        self.__exit__(None, None, None)


    '''
    Add a push button to listen to

    if the callback method returns a function pointer then this function will be called when the button
    is released. Otherwise only a callback on press down will occur.

    Arguments:
    - name: arbitrary name of the button (unique)
    - Callback: function to be called on button press "release_callback callback(str name)"
    - pin: io pin number
    - debounce: The minium time between to clicks (seconds), to avoid bouncing switches
    - io_gnd: set to True if the button connects between io and ground
    - normally_closed: set to False if your switch is shorted when NOT clicked, else True
    '''
    def add_button(self, name, callback, pin, debounce=0.15, io_gnd=True, normally_closed=True):

        if name in [v.name for k, v in self.buttons.iteritems() if k != pin]:
            raise ValueError("Specified name '{}' for button is not unique..".format(name))

        self.gpio.set_pull_up_down(pin, pigpio.PUD_UP if io_gnd else pigpio.PUD_DOWN)

        if not pin in self.buttons.keys():
            cb = self.gpio.callback(pin, pigpio.EITHER_EDGE, self._button_pulse)
        else:
            cb = self.button[pin].iocb

        '''
        rest_level
        +--------------------------+
        | GND  \ NC | True | False |
        |--------------------------|
        | True      |  1   |  0    |
        |--------------------------|
        | False     |  0   |  1    |
        +--------------------------+
        '''
        self.buttons[pin] = self.Button(name, pin, callback, debounce, io_gnd and normally_closed, cb)

    '''
    Add encoders to listen to

    Arguments:
    - name: arbitrary name of the rotary encoder (unique)
    - callback: function to be called on encoder change "callback(int position, int direction)"
    - pinA: first io pins
    - pinB: second io pin
    - io_gnd: set to False if the encoder common pin is connected to 5v, else True if connected to GND
    '''
    def add_rotary_encoder(self, name, callback, pinA, pinB, io_gnd=True):
        if pinA == pinB:
            raise ValueError("pinA and pinB can't be the same...")

        id = tuple(sorted((pinA, pinB)))

        for pair in self.rot_enc.keys():
            if pair == id:
                self.rot_enc[pair].rot_enc.close()
                self.rot_enc.pop(pair)
            elif pinA in pair or pinB in pair:
                raise ValueError("You can't share on io-pin between two rotary encoders")

        if name in [r.name for r in self.rot_enc.values()]:
            raise ValueError("Specified name '{}' for rotary encoder is not unique..".format(name))

        self.rot_enc[id] = self.Encoder(
                RotaryEncoder(self.gpio, callback, (pinA, pinB), io_gnd),
                name)

    '''
    Get the position of a rotary encoder
    '''
    def get_position(self, name):
        id = _find_rotary_encoder(name)
        if id is None:
            raise ValueError("Unknown rotary encoder ''".format(name))

        return self.rot_enc[id].rot_enc.get_position()

    '''
    Set the position of a rotary encoder
    '''
    def set_position(self, name, position):
        id = _find_rotary_encoder(name)
        if id is None:
            raise ValueError("Unknown rotary encoder ''".format(name))

        self.rot_enc[id].rot_enc.set_position(position)

    '''
    Handle a button press
    '''
    def _button_pulse(self, io, level, tick):
        b = self.buttons[io]

        dt_bounce = tick - b.t_last_rising
        if dt_bounce < 0:
            dt_bounce += 2**32

        if level != b.rest_level:
            # Button pushed down, call teh callback method
            b.t_last_rising = tick

            if dt_bounce > b.debounce*1e6:
                b.t_down = tick
                b.release_cb = b.cb(b.name)
        elif b.release_cb:
            # Button released, call release callback if user supplied one at pushdown
            dt_down = tick - b.t_down
            if dt_down < 0:
                dt_down += 2**32

            cb2 = b.release_cb
            b.release_cb = None
            cb2(b.name, dt_down/1e6)

    '''
    Find rotary encoder id by name
    '''
    def _find_rotary_encoder(self, name):
        for id, r in self.rot_enc.iteritems():
            if r.name == name:
                return id
