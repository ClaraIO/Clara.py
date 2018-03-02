#!/usr/bin/env python3

"""Generate cryptographically random alphanumeric strings."""

import string
import random

systemrandom = random.SystemRandom()


def generate_key(size=64, chars=string.digits + string.ascii_letters):
    """Generate a crypographically random string.
    
    * `size` - The length of the string to be generated.
    * `chars` - A list of characters that can be used in the string. Defaults to alphanumeric.
    """
    key = "".join([systemrandom.choice(chars) for n in range(size)])
    return key


if __name__ == "__main__":
    key = generate_key()
    print(key)
