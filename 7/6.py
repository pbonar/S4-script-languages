import logging


logging.basicConfig(level=logging.DEBUG)


def logging_decorator(level=logging.DEBUG):
    def decorator(func):
        def logging_decorator_function(*args, **kwargs):
            ret = func(*args, **kwargs)
            logging.log(level, f"Function {func.__name__} called with args: {args} and kwargs: {kwargs} and returned {ret}")
            return ret

        return logging_decorator_function
    
    return decorator


def main() -> None:
    @logging_decorator(level=logging.WARNING)
    def add(a: int, b: int) -> int:
        return a + b

    @logging_decorator(level=logging.INFO)
    def sub(a: int, b: int) -> int:
        return a - b
    
    @logging_decorator()
    class A:
        def __init__(self):
            pass
        
        def __repr__(self) -> str:
            return "<OBJECT A>"

    add(1, 2)
    sub(1, 2)
    a = A()


if __name__ == "__main__":
    main()
