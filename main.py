import traceback
from dataclasses import dataclass
import sys
from typing import Optional, List
from enum import auto, Enum
import todoist
import json

FILE_PATH = 'TODO.txt'


@dataclass
class TodistAccount:
    token: str


def _set_api(account: TodistAccount) -> todoist.TodoistAPI:
    api = todoist.TodoistAPI(account.token)
    api.sync()
    return api


def _add_task(api: todoist.TodoistAPI, project_id: int, task: str):
    api.items.add(task, project_id=project_id)
    api.commit()


def _add_tasks(api: todoist.TodoistAPI, project_id: int, tasks: List[str]):
    for t in tasks:
        _add_task(api, project_id, t)


def load_account_from_json(path: str) -> TodistAccount:
    with open(path, 'r') as f:
        data = json.load(f)
        if 'token' not in data:
            ValueError('Invalid json file. Expected key `token`')
        return TodistAccount(data['token'])


def update_todist_from_file(account: TodistAccount, path: str, project_name: str) -> bool:
    try:
        api = _set_api(account)
        project_id = next(filter(lambda x: x['name'] == project_name, api.projects.all()))['id']
        with open(path, 'r') as f:
            tasks = [raw_line.replace('-', '').strip() for raw_line in f.readlines()]
        _add_tasks(api, project_id, tasks)
        return True
    except Exception:
        traceback.print_exc()
    return False


def update_file_from_todoist(account: TodistAccount, path: str, project_name: str) -> bool:
    try:
        api = _set_api(account)
        project_id = next(filter(lambda x: x['name'] == project_name, api.projects.all()))['id']
        tasks = [e['content'] for e in api.projects.get_data(project_id)['items']]
        with open(path, 'a') as f:
            f.writelines([f'- {t}\n' for t in tasks])
        return True
    except Exception:
        traceback.print_exc()
    return False


class OpType(Enum):
    PUSH = auto()
    PULL = auto()

USAGE = """USAGE:
  COMMAND:
    push <file_path>: Update todoist account from `file`
    pull <file_path>: Update `file` from todoist account
  
  SUBCOMMAND:
    -c <file_path>: Choose todist account from cutstom .json `file`
    -p <project_name>: Choose todist project to work from"""

if __name__ == '__main__':
    args = list(reversed(sys.argv[1:].copy()))
    path: str = ''
    op: Optional[OpType] = None
    custom: bool = False
    path_to_custom: str = ''
    project_name: str = 'Inbox'
    if len(args) == 0:
        print(USAGE)
        exit(1)
    while len(args) > 0:
        arg = args.pop()
        if arg == 'push':
            if len(args) == 0:
                op = OpType.PUSH
                path = FILE_PATH
            elif len(args) > 0:
                op = OpType.PUSH
                path = args.pop()
            else:
                print('Invalid usage for push command')
                print(USAGE)
                exit(1)
        elif arg == 'pull':
            if len(args) == 0:
                op = OpType.PULL
                path = FILE_PATH
            elif len(args) > 0:
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
        elif arg == '-p':
            if len(args) > 0:
                project_name = args.pop()
            else:
                print('Invalid usage for `-`p` subcommand')
                print(USAGE)
                exit(1)
        else:
            print(f'Unknwon command {arg}')
            exit(1)
    if custom:
        print(f'[INFO] Loading custom account from file: `{path_to_custom}`')
        account = load_account_from_json(path_to_custom)
    else:
        account = load_account_from_json('account.json')
    succeeded: bool = False
    if op == OpType.PUSH:
        print(f'[INFO] Pushing file `{path}` to todoist. Project: {project_name}')
        succeeded = update_todist_from_file(account, path, project_name)
    elif op == OpType.PULL:
        print(f'[INFO] Pulling to file `{path}` from todoist. Project: {project_name}')
        succeeded = update_file_from_todoist(account, path, project_name)
    else:
        raise ValueError(f'Unknown operation {op}. This may be a bug in the parsing of the arguments')
    if succeeded:
        print('[SUCCESS] Succesfully finished execution')
    else:
        print('[ERROR] Execution failed, Try again')
