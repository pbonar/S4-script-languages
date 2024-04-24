from typing import Any, Callable, Iterable


def forall(pred: Callable[[Any], bool], iterable: Iterable) -> bool:
    match iterable:
        case [head, *_] if not pred(head):
            return False
        case [head, *rest]:
            return forall(pred, rest)
        case _:
            return True


def exists(pred: Callable[[Any], bool], iterable: Iterable) -> bool:
    match iterable:
        case [head, *_] if pred(head):
            return True
        case [head, *rest]:
            return forall(pred, rest)
        case _:
            return False


def atleast(n: int, pred: Callable[[Any], bool], iterable: Iterable) -> bool:
    def h(n: int, rest: Iterable, acc: int) -> bool:
        match acc:
            case x if x >= n:
                return True
            case _:
                match rest:
                    case [head, *rest] if pred(head):
                        return h(n, rest, acc+1)
                    case [head, *rest] if not pred(head):
                        return h(n, rest, acc)
                    case _:
                        return False
    
    return h(n, iterable, 0)


def atmost(n: int, pred: Callable[[Any], bool], iterable: Iterable) -> bool:
    def h(n: int, rest: Iterable, acc: int) -> bool:
        match acc:
            case x if x > n:
                return False
            case _:
                match rest:
                    case [head, *rest] if pred(head):
                        return h(n, rest, acc+1)
                    case [head, *rest] if not pred(head):
                        return h(n, rest, acc)
                    case _:
                        return True
    
    return h(n, iterable, 0)


def main() -> None:
    print(forall(lambda x: x == 2, [2, 3, 2]))
    print(exists(lambda x: x == 2, [2, 3, 2]))
    print(atleast(2, lambda x: x == 2, [2, 3, 2]))
    print(atmost(2, lambda x: x == 2, [2, 3, 2]))


if __name__ == "__main__":
    main()
