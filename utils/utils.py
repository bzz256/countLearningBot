import random
from random import randrange


def generate_problem():
    global a, b
    problem = []
    oper = random.choice(["+", "-", "*", "/"])
    if oper == "+":
        a = randrange(10, 99)
        b = randrange(10, 99)
    elif oper == "*":
        a = randrange(2, 9)
        b = randrange(2, 9)
    elif oper == "-":
        a = randrange(10, 99)
        b = 100
        while b > a:
            b = randrange(2, 99)
    elif oper == "/":
        b = randrange(2, 9)
        a = randrange(2, 9) * b
    problem.append(str(a))
    problem.append(oper)
    problem.append(str(b))
    problem.append(int(eval(" ".join(problem))))
    return problem
