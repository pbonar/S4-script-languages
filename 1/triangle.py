a: int
h: int

try:
    a = int(input("a = "))
    h = int(input("h = "))
except:
    print("Wrong input!")
    exit()

if a < 0 or h < 0:
    print("a and h must be >= 0")
    exit()

print(f"Area = {a*h/2}")
