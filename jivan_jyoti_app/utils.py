import re


def validate_pin(pin):
    p = re.compile('^(\d{6})$')
    if re.match(p, pin):
        return True
    else:
        return False


def mobile_valid(s):
    pattern = re.compile("^([7-9][0-9]{9})$")
    return pattern.match(s)
