# -*- coding: utf-8 -*-


def greet(name):
    first_name, surname = name.split(' ')
    return 'Hello {0}, {1}'.format(surname, first_name)