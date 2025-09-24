def calculate_sr(numbers):
    if not numbers:
        return print("No numbers provided")
    return print(f"{sum(numbers) / len(numbers):.2f}")

def stringProcessing(input_string):
    if not input_string:
        return print("No input provided")
    return print(f"""Processed string:\n
                Length: {len(input_string)}\n
                First+Last characters: {input_string[0]}{input_string[-1]}\n
                StringUp: {input_string.upper()}\n
                RepeatString3: {input_string * 3}""")

def listProcessing(input_list):
    if not input_list:
        return print("No input provided")
    return print(f"""Processed list:
                Second element: {input_list[1]}
                Length: {len(input_list)}
                Last 3 elements: {input_list[-3:]}
                Change 3rd element: {input_list[:2] + ['Python'] + input_list[3:]}""")

def uniqueElements(input_list):
    if not input_list:
        return print("No input provided")
    return print(f"""Processed list:
                List: {input_list}
                Set : {set(input_list)}""")

def informationAboutStudents(input_dict):
    if not input_dict:
        return print("No input provided")
    print(f"""Студент: {input_dict['Имя'].strip()} {input_dict['Фамилия'].strip()}
Возраст: {input_dict['Возраст'].strip()}
Курс: {input_dict['Курс'].strip()}""")
    return

def checkEven(input_number):
    if input_number % 2 == 0:
        return print(f"True")
    else:
        return print(f"False")

def simpleCalculator(num1, num2, operation):
    if operation == "+":
        return print(f"Result: {num1 + num2}")
    elif operation == "-":
        return print(f"Result: {num1 - num2}")
    elif operation == "*":
        return print(f"Result: {num1 * num2}")
    elif operation == "/":
        if num2 != 0:
            return print(f"Result: {num1 / num2}")
        else:
            return print("Error: Division by zero is not allowed.")
    else:
        return print("Error: Invalid operation.")
    
while True:
    task = input("Enter task (1-7) or 'exit' to quit: ")
    if task == "1":
        numbers = list(map(int, input("Enter numbers separated by spaces: ").split()))
        calculate_sr(numbers)
    elif task == "2":
        input_string = input("Enter a string: ")
        stringProcessing(input_string)
    elif task == "3":
        input_list = list(input("Enter a list of elements separated by spaces: ").split())
        listProcessing(input_list)
    elif task == "4":
        input_list = list(input("Enter a list of elements separated by spaces: ").split())
        uniqueElements(input_list)
    elif task == "5":
        input_dict = {}
        while True:
            entry = input("Enter student name and grade (or 'done' to finish): ")
            if entry == "done":
                break
            name, grade = entry.split()
            input_dict[name] = grade
        informationAboutStudents(input_dict)
    elif task == "6":
        input_number = int(input("Enter a number: "))
        checkEven(input_number)
    elif task == "7":
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        operation = input("Enter operation (+, -, *, /): ")
        simpleCalculator(num1, num2, operation)
    elif task == "exit":
        break
    else:
        print("Invalid task. Please try again.")
