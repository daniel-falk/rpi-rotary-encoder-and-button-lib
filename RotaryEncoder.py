import pigpio

class RotaryEncoder:

    '''
    RotaryEncoder constructor

    Arguments:
    - gpio: a pigpio pi object
    - callback: function to be called on encoder change callback(int position, int direction)
    - pin_pair: tuple with the two encoder ouutput io pins
    - io_gnd: set to False if the encoder common pin is connected to 5v, else True if connected to GND
    '''
    def __init__(self, gpio, callback, pin_pair, io_gnd=True):
        self.gpio = gpio
        self.pins = pin_pair
        self.callback = callback

        self.cbs = []
        for io in self.pins:
            gpio.set_mode(io, pigpio.INPUT)
            gpio.set_pull_up_down(io, pigpio.PUD_UP if io_gnd else pigpio.PUD_DOWN)
            self.cbs.append(gpio.callback(io, pigpio.EITHER_EDGE, self._pulse))

        self.last_io = None
        self.level = dict([(io, gpio.read(io)) for io in self.pins])

        self.position = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for cb in self.cbs:
            cb.cancel()

    def close(self):
        self.__exit__(None, None, None)

    '''
    Get the position of the encoder
    '''
    def get_position(self):
        return self.position

    '''
    Set the position of the encoder
    '''
    def set_position(self, position):
        self.position = position

    '''
    Deal with the encoder pulses and call the specified callback
    '''
    def _pulse(self, io, level, tick):
        if io != self.last_io:
            self.last_io = io
            self.level[io] = level

            other = [v for v in self.pins if v != io][0]
            factor = 1 if io == self.pins[0] else -1
            diff = (1 if level != self.level[other] else -1) * factor
            self.position += diff

            self.callback(self.position, diff)


