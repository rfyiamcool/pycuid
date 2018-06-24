# coding:utf-8
import os
import random
import socket
import time


BASE = 36
BLOCK_SIZE = 4
DISCRETE_VALUES = BASE ** BLOCK_SIZE


_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
def _to_base36(number):
    if number < 0:
        raise ValueError("Cannot encode negative numbers")

    chars = ""
    while number != 0:
        number, i = divmod(number, 36)  # 36-character alphabet
        chars = _ALPHABET[i] + chars

    return chars or "0"


_PADDING = "000000000"
def _pad(string, size):  # type: (str, int) -> str
    strlen = len(string)
    if strlen == size:
        return string
    if strlen < size:
        return _PADDING[0:size-strlen] + string
    return string[-size:]


def _random_block():  # type: () -> str
    """
    Generate a random string of `BLOCK_SIZE` length.
    :rtype: str
    """
    random_number = random.randint(0, DISCRETE_VALUES)
    random_string = _to_base36(random_number)
    return _pad(random_string, BLOCK_SIZE)


def get_process_fingerprint():  # type: () ->  str
    pid = os.getpid()
    hostname = socket.gethostname()
    padded_pid = _pad(_to_base36(pid), 2)
    hostname_hash = sum([ord(x) for x in hostname]) + len(hostname) + 36
    padded_hostname = _pad(_to_base36(hostname_hash), 2)
    return padded_pid + padded_hostname


_GENERATOR = None  # type: CuidGenerator

def _generator():  # type: () -> CuidGenerator
    global _GENERATOR
    if not _GENERATOR:
        _GENERATOR = CuidGenerator()
    return _GENERATOR


def cuid():  # type: () -> str
    """
    :rtype: str
    """
    return _generator().cuid()


def slug():  # type: () -> str
    """
    :rtype: str
    """
    return _generator().slug()


class CuidGenerator(object):

    def __init__(self, fingerprint=None):
        # type: (str) -> None
        """
        :param str fingerprint: process fingerprint to use
        """
        self.fingerprint = fingerprint or get_process_fingerprint()
        self._counter = -1
        self.last_ts = int(time.time() * 1000)

    def diff_clock(self, ts):
        if ts < self.last_ts:
            return False
        return True

    @property
    def counter(self):
        # type: () -> int
        """
        Rolling counter that ensures same-machine and same-time
        cuids don't collide.
        :return: counter value
        :rtype: int
        """
        self._counter += 1
        if self._counter >= DISCRETE_VALUES:
            self._counter = 0
        return self._counter

    def cuid(self):
        # type: () -> str
        """
        Generate a full-length cuid as a string.
        :rtype: str
        """
        # start with a hardcoded lowercase c
        identifier = "c"
        # add a timestamp in milliseconds since the epoch, in base 36
        millis = int(time.time() * 1000)
        while self.diff_clock(millis) == False:
            time.sleep(0.00001)

        self.last_ts = millis
        identifier += _to_base36(millis)
        # use a counter to ensure no collisions on the same machine
        # in the same millisecond
        count = _pad(_to_base36(self.counter), BLOCK_SIZE)
        identifier += count
        # add the process fingerprint
        identifier += self.fingerprint
        # add a couple of random blocks
        identifier += _random_block()
        identifier += _random_block()

        return identifier

    def slug(self):
        """
        :rtype: str
        """
        identifier = ""
        # use a truncated timestamp
        millis = int(time.time() * 1000)
        millis_string = _to_base36(millis)
        identifier += millis_string[-2:]
        # use a truncated counter
        count = _pad(_to_base36(self.counter), 1)
        identifier += count
        # use a truncated fingerprint
        identifier += self.fingerprint[0]
        identifier += self.fingerprint[-1]
        # use some truncated random data
        random_data = _random_block()
        identifier += random_data[-2:]

        return identifier


if __name__ == "__main__":
    g = CuidGenerator()
    print g.cuid()
    print g.slug()

