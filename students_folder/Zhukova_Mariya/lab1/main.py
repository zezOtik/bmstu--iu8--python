
if __name__ == '__main__':
    print("Введите строку, нажмите Enter чтобы отправить:")
    user_str = str(input())
    print("Длина введенной пользователем строки", len(user_str))
    print("Строка, приведенная к верхнему регистру", user_str.upper())
    print("Три раза продублированная строка", user_str * 3)
