some_list = [1, "hello", 3, "world", 5]

print(f'Second element is: {some_list[1]}')
print(f'Len is: {len(some_list)}')
print(f'Last three element is: {some_list[len(some_list) - 3:]}')

print(f'List before update: {some_list}')
some_list[2] = "Python"
print(f'List after update: {some_list}')
