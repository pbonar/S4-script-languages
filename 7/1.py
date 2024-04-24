from typing import Final


def acronym(xs: list[str]) -> str:
    return "" if len(xs) == 0 else xs[0][0] + acronym(xs[1:])


def median(xs: list[int]) -> float:
    sorted_xs: Final[list[int]] = sorted(xs)
    
    return (
        sorted_xs[len(xs) // 2]
    ) if len(xs) % 2 != 0 else (
        (sorted_xs[len(xs) // 2] + sorted_xs[len(xs) // 2 - 1]) / 2
    )


def my_sqrt(x: float, epsilon: float) -> float:
    def h(x: float, prev: float, epsilon: float) -> float:
        next: Final[float] = prev - (prev - x/prev)/2
        
        return abs(next) if abs(next**2 - x) < epsilon else h(x=x, prev=next, epsilon=epsilon)

    return h(x=x, prev=x/2, epsilon=epsilon)


def make_alpha_dict(s: str) -> dict[str, list[str]]:
    return {
        c: [x for x in s.split() if c in x] for c in s if c != " "
    }
    

def flatten(xs: list | tuple) -> list:
    return (
        [a for i in xs for a in flatten(i)]
    ) if isinstance(xs, (list, tuple)) else (
        [xs]
    )


def main() -> None:
    print(acronym(["Zakład", "Ubezpieczeń", "Społecznych"]))
    print(median([1,1,19,2,3,4,4,5,1]))
    print(my_sqrt(3, epsilon=0.1), my_sqrt(81, epsilon=0.01))
    print(make_alpha_dict("on i ona"))
    print(flatten([[1, 2, (3, 'a')], [5, [6.5, 7, [8]]], 9]))


if __name__ == "__main__":
    main()
    