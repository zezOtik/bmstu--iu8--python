first_number = float(input("Enter first number: "))
second_number = float(input("Enter second number: "))

operation = input("Enter operation: ")
if operation == "+":
    print(f'Result is: {first_number + second_number}')
elif operation == "-":
    print(f'Result is: {first_number - second_number}')
elif operation == "*":
    print(f'Result is: {first_number * second_number}')
elif operation == "/":
    if second_number == 0:
        print("Can't divide by zero")
        exit()
    print(f'Result is: {first_number / second_number}')
else:
    print("Invalid operation")