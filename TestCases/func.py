import random
import string


def generate_random_string(length, dtype):
    if dtype == int:
        digits = string.digits
        random_string = ''.join(random.choice(digits) for i in range(length))
    else:
        letters_and_digits = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(letters_and_digits) for i in range(length))
    return random_string

print(generate_random_string(30,"string")+"@gmail.com")