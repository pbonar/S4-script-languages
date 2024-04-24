from typing import Any, Callable, Generator


def make_generator(f: Callable[[Any], Generator]) -> Generator:
    i = 1
    while True:
        yield f(i)
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
        
        generator = make_generator(func)
        for i, x in enumerate(generator):
            print(x)
            
            if i == 5:
                break


if __name__ == "__main__":
    main()    
