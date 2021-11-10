import os.path
import traceback
from dataclasses import dataclass
import sys
from typing import Optional, List, Tuple
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
    if not os.path.exists(path):
        print(f'[ERROR] Coulnn\'t find path `{path}`')
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


OP_NAMES = {'push': OpType.PUSH, 'pull': OpType.PULL}


def load_config_from_json(path: str) -> Tuple[TodistAccount, str, OpType, str]:
    with open(path, 'r') as f:
        data = json.load(f)
        for k in ('account', 'project', 'action', 'file_path'):
            if k not in data:
                print(f'[ERROR] Missing key `{k}` in config file `{path}`')
                exit(1)
        return load_account_from_json(data['account']), data['file_path'], OP_NAMES[data['action']], data['project']


def load_config_from_args(args: List[str]) -> Tuple[TodistAccount, str, OpType, str]:
    if len(args) == 0:
        print(USAGE)
        exit(1)
    path: str = FILE_PATH
    account_path: str = 'accounts.pydone.json'
    project_name: str = 'Inbox'
    op: Optional[OpType] = None
    while len(args) > 0:
        arg = args.pop()
        if arg == 'push':
            if len(args) == 0:
                op = OpType.PUSH
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
            elif len(args) > 0:
                op = OpType.PULL
                path = args.pop()
            else:
                print('Invalid usage for pull command')
                print(USAGE)
                exit(1)
        elif arg == '-c':
            if len(args) > 0:
                account_path = args.pop()
            else:
                print('Invalid usage for `-c` subcommand')
                print(USAGE)
                exit(1)
        elif arg == '-p':
            if len(args) > 0:
                project_name = args.pop()
            else:
                print('Invalid usage for `-p` subcommand')
                print(USAGE)
                exit(1)
        elif arg == '-config':
            if len(args) > 0:
                config_path = args.pop()
                return load_config_from_json(config_path)
            else:
                print('Invalid usage for `-config` subcommand')
                print(USAGE)
                exit(1)
        else:
            print(f'Unknwon command {arg}')
            exit(1)
    else:
        print(f'[INFO] Loading account from file: `{account_path}`')
        account = load_account_from_json(account_path)
    return account, path, op, project_name


USAGE = """USAGE:
  FLAG:
    --config: Use file named config.pydone.json to carry out execution
  COMMAND:
    push <file_path>: Update todoist account from `file`. If no file is provided the default is 'TODO.txt'
    pull <file_path>: Update `file` from todoist account. If no file is provided the default is 'TODO.txt'
  
  SUBCOMMAND:
    -c <file_path>: Choose todist account from cutstom .json `file`
    -p <project_name>: Choose todist project to work from"""

if __name__ == '__main__':
    args = list(reversed(sys.argv[1:].copy()))
    op: Optional[OpType] = None
    custom: bool = False
    config_path = 'config.pydone.json'
    if '--config' in args:
        if os.path.exists(config_path):
            print(f'[INFO] Loading config from file: `{config_path}`')
            account, path, op, project_name = load_config_from_json(config_path)
        else:
            account, path, op, project_name = load_config_from_args(args)
    else:
        account, path, op, project_name = load_config_from_args(args)
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
