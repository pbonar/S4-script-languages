import os
import sys


def get_vars() -> list[str]:
    if len(sys.argv) > 1:
        res = []
        
        for env in os.environ:
            # check if included in some param
            includes = False
            for arg in sys.argv[1:]:
                if arg in env:
                    includes = True
            
            if includes:
                res.append(env)
        
        return res
    else:
        # return all
        return list(os.environ.keys())

def main() -> None:
    vars_to_print = sorted(get_vars())
    for env_name in vars_to_print:
        print(env_name, "=", os.environ[env_name])


if __name__ == "__main__":
    main()
