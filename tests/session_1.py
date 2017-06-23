# -*- coding: utf-8 -*-


def greet(name):
    first_name, surname = name.split(' ')
    return 'Hello {0}, {1}'.format(surname, first_name)

	
def suggest_travel(distance):
	i = 0
	while True:
		i += 1

def fizz_buzz(n):
    if n%3==0 and n%5==0:
        return 'FizzBuzz'
    elif n%3==0:
        return 'Fizz'
    elif n%5==0:
        return 'Buzz'
    else:
        return n


def sum_odd():
    my_sum=0
    for n in range(1,100):
        if n%2!=0:
            my_sum = my_sum + n
    return my_sum


def sum_div3():
    my_sum=0
    for n in range(1,100):
        if n%3==0:
            my_sum = my_sum + n
    return my_sum


def sum_all():
    my_sum=0
    for n in range(1,100):
        my_sum = my_sum + n
    return my_sum