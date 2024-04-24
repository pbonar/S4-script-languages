import random
from string import ascii_letters, digits

class PasswordGenerator:
    counter: int
    
    length: int
    charset: str
    count: int
    
    def __init__(self, length: int, charset: str = ascii_letters + digits, count: int = 10):
        self.length = length
        self.charset = charset
        self.count = count
        
        self.counter = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.counter >= self.count:
            raise StopIteration
        else:
            self.counter += 1
            return ''.join([random.choice(self.charset) for _ in range(self.length)])
    

def main() -> None:
    generator = PasswordGenerator(length=8, count=5)
    
    for password in generator:
        print(password)

    generator_2 = PasswordGenerator(length=10, charset="KOT123", count=2)
    
    while True:
        try:
            print(generator_2.__next__())
        except StopIteration:
            break


if __name__ == "__main__":
    main()
    