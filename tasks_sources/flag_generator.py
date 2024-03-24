#! /usr/bin/env python3

from random import choices
from string import ascii_lowercase, digits

def generate_flag():
    return f"flag_{{{''.join(choices(ascii_lowercase + digits, k = 10))}}}"

print(generate_flag())
