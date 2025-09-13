set_data = {
    'Имя':"Alexey",
    'Фамилия':"Zemliakov",
    'Возраст':21,
    'Курс':1
}

full_name = set_data['Имя'] + " " + set_data['Фамилия']

print(f'Студент: {full_name}')
print(f'Возраст: {set_data["Возраст"]}')
print(f'Курс: {set_data["Курс"]}')