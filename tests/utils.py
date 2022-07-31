from random import choice
from string import ascii_letters, ascii_lowercase, ascii_uppercase

CHARACTERS = ascii_letters + ascii_lowercase + ascii_uppercase


def randstr(length: int = 10) -> str:
    return ''.join(choice(CHARACTERS) for _ in range(length))
