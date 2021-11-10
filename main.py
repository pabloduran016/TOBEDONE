from dataclasses import dataclass
import sys
from typing import Optional
from enum import auto, Enum

FILE_PATH = 'TODO.txt'


@dataclass
class TodistAccount:
    pass


DEFAULT_ACCOUNT = TodistAccount()


def load_account_from_json(path: str) -> TodistAccount:
    raise NotImplementedError


def update_todist_from_file(path: str, account: TodistAccount) -> bool:
    raise NotImplementedError


def update_file_from_todoist(path: str, account: TodistAccount) -> bool:
    raise NotImplementedError


class OpType(Enum):
    PUSH = auto()
    PULL = auto()

USAGE = """USAGE:
  COMMAND:
    push <file_path>: update todoist account from `file`
    pull <file_path>: update `file` from todoist account
  
  SUBCOMMAND:
    -c <file_path>: Choose todist account from cutstom .json `file`"""

if __name__ == '__main__':
    args = list(reversed(sys.argv[1:].copy()))
    path: str = ''
    op: Optional[OpType] = None
    custom: bool = False
    path_to_custom: str = ''
    if len(args) == 0:
        print(USAGE)
        exit(1)
    while len(args) > 0:
        arg = args.pop()
        if arg == 'push':
            if len(args) > 0:
                op = OpType.PUSH
                path = args.pop()
            else:
                print('Invalid usage for push command')
                print(USAGE)
                exit(1)
        elif arg == 'pull':
            if len(args) > 0:
                op = OpType.PULL
                path = args.pop()
            else:
                print('Invalid usage for pull command')
                print(USAGE)
                exit(1)
        elif arg == '-c':
            if len(args) > 0:
                custom = True
                path_to_custom = args.pop()
            else:
                print('Invalid usage for `-c` subcommand')
                print(USAGE)
                exit(1)
        else:
            print(f'Unknwon command {arg}')
            exit(1)
    if custom:
        print(f'[INFO] Loading custom account from file: `{path_to_custom}`')
        account = load_account_from_json(path_to_custom)
    else:
        account = DEFAULT_ACCOUNT
    succeeded: bool = False
    if op == OpType.PUSH:
        print(f'[INFO] Pushing file `{path}` to todoist')
        succeeded = update_todist_from_file(path, account)
    elif op == OpType.PULL:
        print(f'[INFO] Pulling to file `{path}` from todoist')
        succeeded = update_file_from_todoist(path, account)
    else:
        raise ValueError(f'Unknown operation {op}. This may be a bug in the parsing of the arguments')
    if succeeded:
        print('[SUCCESS] Succesfully finished exedcution')
    else:
        print('[ERROR] Execution failed, Try again')
