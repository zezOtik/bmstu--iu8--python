a = int(input())
b = int(input())
c = int(input())
print(round((a + b + c) / 3, 2))

st = input()
print(len(st), f"first -- {st[0]}, last -- {st[-1]}", st.upper(), st*3, sep="\n")

example_list = [1, "test", 23, 57, "another string"]
print(example_list[1], len(example_list), example_list[-3:], sep="\n")
print(f"Before change -- {example_list[2]}")
example_list[2] = "Python"
print(f"After change -- {example_list[2]}")

nums = input()
nums_list = nums.split(" ")
set = {num for num in nums_list}
print(nums_list, set, sep="\n")

dict = {
    'Студент': input(),
    'Возраст': input(),
    'Курс': input()
}

for key in dict:
    print(f"{key}: {dict[key]}")

num = int(input())
print(num % 2 == 0)

num1 = input()
num2 = input()
op = input()

print(eval(num1 + op + num2))