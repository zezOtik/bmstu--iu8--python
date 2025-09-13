data = input("Enter a string: ")

print(f'The string len is: {len(data)}')
if len(data) > 0:
    print(f'The first symbol is: {data[0]}, the last is: {data[-1]}')
else:
    print("The string is empty, no first and last symbols")

print(f'Upper string: {data.upper()}')

print(f'Triple string: {data*3}')