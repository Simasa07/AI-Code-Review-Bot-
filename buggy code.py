def divide_numbers(a, b):
    return a / b


def get_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total / len(numbers)


password = "admin123"


def check_login(username, pw):
    if pw == password:
        return True
    else:
        return False


items = []
def add_item(x):
    items.append(x)
    return items
