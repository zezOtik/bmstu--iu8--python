data = input('input numbers: ')

data = data.split(" ")
numbers = []

for i in data:
    if i.isdigit():
        numbers.append(int(i))

print(f'input list: {numbers}')
print(f'output set: {set(numbers)}')