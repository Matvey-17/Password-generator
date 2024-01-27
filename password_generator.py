import random
from random import choice

import string

ally = string.digits + string.ascii_uppercase + string.ascii_lowercase + string.punctuation


def generator_password(len_password, password=''):
    password += choice(string.ascii_uppercase)
    for _ in range(len_password - 1):
        password += choice(ally)
    if not (any(digit in password for digit in string.digits)):
        index_digit = random.randint(0, len_password)
        digit = random.choice(string.digits)
        password = list(password)
        password.pop(index_digit)
        password.insert(index_digit, digit)
        password = ''.join(password)
    return password
