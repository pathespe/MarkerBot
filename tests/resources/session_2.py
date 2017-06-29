def longer_string(string1, string2):
	if len(string1) > len(string2):
		return string1
	else:
		return string2

def print_triangle(height):
	for i in range(height):
		print('*'*(i+1))