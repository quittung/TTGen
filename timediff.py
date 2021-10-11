def time_read(txt):
    minute = int(txt[:2])
    second = int(txt[2:])
    return minute * 60 + second

while True:
    txt = input()
    txt1, txt2 = txt.split("-")
    t1 = time_read(txt1)
    t2 = time_read(txt2)

    print(t1 - t2)

