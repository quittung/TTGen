def time_read(txt):
    minute = int(txt[:2])
    second = int(txt[2:])
    return minute * 60 + second

print("Calculates difference between to timestamps.")
print("Format: mmss-mmss")
while True:
    txt = input("Enter expression: ")
    txt1, txt2 = txt.split("-")
    t1 = time_read(txt1)
    t2 = time_read(txt2)

    delta = t1 - t2
    if delta < 0: delta += 3600

    print("{:.0f}\n".format(delta))

