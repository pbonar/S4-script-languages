from functools import cache
from typing import Any, Callable, Generator


# idk czy to o to chodzi, trochę niezrozumiałe polecenie??
@cache
def make_generator_mem(f: Callable[[Any], Generator]) -> Generator:
    cached = {}
    
    i = 1
    while True:
        if i not in cached:
            cached[i] = f(i)
        
        yield cached[i]
        i += 1


def main() -> None:
    def fib(n: int) -> int:
        return n if n < 2 else fib(n-1) + fib(n-2)

    lambdas = {
        "fib": fib,
        "square": lambda n: n**2,
        "cube": lambda n: n**3
    }
    
    for name, func in lambdas.items():
        print(f">> {name}")
        
        generator = make_generator_mem(func)
        for i, x in enumerate(generator):
            print(x)
            
            if i == 5:
                break


if __name__ == "__main__":
    main()
