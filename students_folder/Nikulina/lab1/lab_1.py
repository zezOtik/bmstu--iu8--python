students = []
n = int(input("Введите количество студентов для ввода: "))
for i in range(n):
    print(f"\nСтудент {i+1}:")
    student = {
        "имя": input("Введите имя: "),
        "фамилия": input("Введите фамилию: "),
        "возраст": int(input("Введите возраст: ")),
        "курс": int(input("Введите курс: "))
    }
    students.append(student)
for s in students:
    print(f"\nСтудент: {s['имя']} {s['фамилия']}")
    print(f"Возраст: {s['возраст']}")
    print(f"Курс: {s['курс']}")
