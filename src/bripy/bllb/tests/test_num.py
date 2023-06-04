from bripy.bllb.num import Num


def test_num():
    nums = list(map(Num, range(10)))
    print(nums)
    print(Num(10))
    print(Num(10)[5])
    print(Num(10)[[2, 3]])
    print(Num(10)[slice(2, 5)])

    print(Num(5) @ Num(3))
    print(list("abc")[Num(1)])
    print(Num(2) + 2j)

    for _ in Num(3):
        print(repr(_))

    num = Num(10)
    print(num)
    print(num[5])
    print(num[[2, 3]])
    print(num[slice(2, 5)])
    print(list(num))

    for _ in range(3):
        print(repr(_), next(num))

    for _ in num:
        print(repr(_))
        break

    for _ in num:
        print(repr(_))
        break

    print(list(num))
