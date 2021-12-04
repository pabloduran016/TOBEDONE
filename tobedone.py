import os.path
# import time
import traceback
from dataclasses import dataclass
import sys
from typing import Optional, List, Tuple, Dict
from enum import auto, Enum
from todoist.api import TodoistAPI
import json
import datetime


FILE_PATH = 'TODO.txt'
Task = Dict[str, str]
DAT_FMT = '%Y-%m-%d:%H:%M:%S'
TaskId = int


def _tasks_from_strs(api: TodoistAPI, project_id: int, tstrs: List[str]) -> Dict[str, Task]:
    tasks = {k: None for k in tstrs}
    for t in api.projects.get_data(project_id)['items']:
        if t['content'] in tasks:
            tasks[t['content']] = t
    return tasks


def _tasks_from_ids(api: TodoistAPI, tstrs: List[Tuple[str, TaskId]]) -> Dict[str, Task]:
    return {k: api.items.get_by_id(t_id) for  k, t_id in tstrs}


@dataclass
class TodistAccount:
    token: str


def _set_api(acc: TodistAccount) -> TodoistAPI:
    api = TodoistAPI(acc.token)
    api.sync()
    return api


def _add_task(api: TodoistAPI, project_id: int, task: str, commit: bool = True):
    if task.strip() == '':
        return
    api.items.add(task, project_id=project_id)
    if commit:
        api.commit()



def _modify_task(api: TodoistAPI, t_id: TaskId, task: str, commit: bool = True):
    if task.strip() == '':
        return
    api.items.get_by_id(t_id).update(content=task)
    if commit:
        api.commit()


def _complete_task(api: TodoistAPI, task: Task, commit: bool = True):
    api.items.complete(task['id'], datetime.datetime.today().strftime('%Y-%m-%d'))
    if commit:
        api.commit()


def _add_tasks(api: TodoistAPI, project_id: int, tasks: List[Tuple[str, TaskId]], commit: bool = True):
    for t, t_id in tasks:
        _add_task(api, project_id, t, commit=False)
    if commit:
        api.commit()


def _modify_tasks(api: TodoistAPI, tasks: List[Tuple[str, TaskId]], commit: bool = True):
    for t, t_id in tasks:
        _modify_task(api, t_id, t, commit=False)
    if commit:
        api.commit()


def _complete_tasks(api: TodoistAPI, project_id: int, tasks: List[Tuple[str, TaskId]], commit: bool = True):
    ts = _tasks_from_ids(api, tasks)
    # ts = _tasks_from_strs(api, project_id, current_tasks)
    if len(tasks) == 0:
        return
    for st, t in ts.items():
        _complete_task(api, t, commit=False)
    if commit:
        api.commit()


def load_account_from_json(file_path: str) -> TodistAccount:
    if not os.path.exists(file_path):
        print(f'[ERROR] Couldn\'t find account path `{file_path}`. Try setting it with the `-acc` arg or use `--config`')
        sys.exit(1)
    with open(file_path, 'r') as f:
        data = json.load(f)
        if 'token' not in data:
            ValueError('Invalid json file. Expected key `token`')
        return TodistAccount(data['account_token'])


def sync_file_with_todoist(acc: TodistAccount, file_path: str, project_name: str) -> bool:
    try:
        api = _set_api(acc)
        a = update_todist_from_file(acc, file_path, project_name, set_api=False, api=api)
        b = update_file_from_todoist(acc, file_path, project_name, set_api=False, api=api)
        return a and b
    except Exception:
        traceback.print_exc()
        return False


def _parse_cont_id_from_line(line: str) -> Tuple[str, Optional[TaskId]]:
    r_line = line[::-1]  # reverse the line to strat looking from the traceback
    id_sub_identifier = '(id#'[::-1]  # reverse the sub string identifier aswell
    id_end_identifier = ')'[::-1]  # reverse the end identifier aswell
    end = r_line.find(id_end_identifier)
    if end < 0:
        return None
    start = r_line.find(id_sub_identifier, end)
    if start < 0:
        return None
    val = r_line[end + len(id_end_identifier):start][::-1]  # Don't forget to reverse the output as well
    if val.isnumeric():
        return (r_line[:end].strip() + ' ' + r_line[start + len(id_sub_identifier):].strip())[::-1].strip(), int(val)
    else:
        raise ValueError(f'Corrupted value of id. Expected initiger-like, found {val}')

def update_todist_from_file(acc: TodistAccount, file_path: str, project_name: str, set_api: bool = True,
                            api: Optional[TodoistAPI] = None) -> bool:
    try:
        if set_api:
            api = _set_api(acc)
        else:
            if api is None:
                TypeError('missing paramater api for set_api = False')
        # n1 = time.time()
        project_id = next(filter(lambda x: x['name'] == project_name, api.projects.all()))['id']
        crossed_tasks: List[Tuple[str, TaskId]] = []
        new_tasks: List[Tuple[str, TaskId]] = []
        modified_tasks: List[Tuple[str, TaskId]] = []
        # n2 = time.time()
        current_tasks = []
        completed_tasks = {e['task_id'] for e in api.completed.get_all(project_id=project_id)['items']}
        current_tasks_id = []
        for e in api.projects.get_data(project_id)['items']:
            current_tasks.append(e['content'])
            current_tasks_id.append(e['id'])
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for raw_line in f.readlines():
                    raw_line = raw_line.strip()
                    cont = raw_line[1:].strip()
                    if raw_line.startswith('x'):
                        crossed_tasks.append(_parse_cont_id_from_line(cont))
                    elif raw_line.startswith('-'):
                        ans = t, t_id = _parse_cont_id_from_line(cont)
                        if t_id in completed_tasks:
                            continue
                        elif t_id is None or t_id not in current_tasks_id:
                            new_tasks.append(ans)
                        elif t not in current_tasks:
                            modified_tasks.append(ans)
                    else:
                        print('[WARNING] Invalid TODO. Didn\'t get `-` nor `x` at the beginning')
        _add_tasks(api, project_id, new_tasks)
        _modify_tasks(api, modified_tasks)
        _complete_tasks(api, project_id, crossed_tasks)
        # n3 = time.time()
        # print(f'Took {n2 - n1} seconds to get project id and tasks and {n3 - n2} seconds to add the tasks')
        return True
    except Exception:
        traceback.print_exc()
    return False


def update_file_from_todoist(acc: TodistAccount, file_path: str, project_name: str, set_api: bool = True,
                             api: Optional[TodoistAPI] = None) -> bool:
    try:
        if set_api:
            api = _set_api(acc)
        else:
            if api is None:
                TypeError('missing paramater api for set_api = False')
        project_id = next(filter(lambda x: x['name'] == project_name, api.projects.all()))['id']
        tasks = [(e['content'], e['id']) for e in api.projects.get_data(project_id)['items']]
        with open(file_path, 'w') as f:
            f.writelines([f'- {t} (id#{t_id})\n' for t, t_id in tasks])
        return True
    except Exception:
        traceback.print_exc()
    return False


class OpType(Enum):
    PUSH = auto()
    PULL = auto()
    SYNC = auto()


OP_NAMES = {'push': OpType.PUSH, 'pull': OpType.PULL, 'sync': OpType.SYNC}
OP_HUMAN_NAMES = {OpType.PUSH: 'push', OpType.PULL: 'pull', OpType.SYNC: 'sync'}


def load_config_from_json(file_path: str) -> Tuple[TodistAccount, str, OpType, str]:
    with open(file_path, 'r') as f:
        data = json.load(f)
        for k in ('account_token', 'project', 'action', 'file_path'):
            if k not in data:
                print(f'[ERROR] Missing key `{k}` in config file `{file_path}`')
                sys.exit(1)
        return TodistAccount(data['account_token']), data['file_path'], OP_NAMES[data['action']], data['project']


def load_config_from_args(args: List[str]) -> Tuple[TodistAccount, str, OpType, str]:
    if len(args) == 0:
        print(USAGE)
        sys.exit(1)
    file_path: str = FILE_PATH
    account_path: str = 'accounts.tobedone.json'
    project_name: str = 'Inbox'
    action: Optional[OpType] = None
    while len(args) > 0:
        arg = args.pop()
        if arg == 'push':
            if len(args) == 0:
                action = OpType.PUSH
            elif len(args) > 0:
                if not args[-1].startswith('-'):
                    file_path = args.pop()
                action = OpType.PUSH
            else:
                print('Invalid usage for push command')
                print(USAGE)
                sys.exit(1)
        elif arg == 'pull':
            if len(args) == 0:
                action = OpType.PULL
            elif len(args) > 0:
                if not args[-1].startswith('-'):
                    file_path = args.pop()
                action = OpType.PULL
            else:
                print('Invalid usage for pull command')
                print(USAGE)
                sys.exit(1)
        elif arg == 'sync':
            if len(args) == 0:
                action = OpType.SYNC
            elif len(args) > 0:
                if not args[-1].startswith('-'):
                    file_path = args.pop()
                action = OpType.SYNC
            else:
                print('Invalid usage for sync command')
                print(USAGE)
                sys.exit(1)
        elif arg == '-acc':
            if len(args) > 0 and not args[-1].startswith('-'):
                account_path = args.pop()
            else:
                print('Invalid usage for `-acc` subcommand')
                print(USAGE)
                sys.exit(1)
        elif arg == '-p':
            if len(args) > 0 and not args[-1].startswith('-'):
                project_name = args.pop()
            else:
                print('Invalid usage for `-p` subcommand')
                print(USAGE)
                sys.exit(1)
        else:
            print(f'Unknwon command {arg}')
            sys.exit(1)
    # print(f'[INFO] Loading account from file: `{account_path}`')
    acc = load_account_from_json(account_path)
    assert action is not None
    return acc, file_path, action, project_name


USAGE = """USAGE: python main.py [OPTINAL FLAGS] <COMMAND> [ARGS] 
  OPTIONAL FLAGS:
    --config <file>: Use file named config.tobedone.json or `file` if provided to carry out execution
  COMMAND:
    push <file>: Update todoist account from `file`. If no file is provided the default is 'TODO.txt'
    pull <file>: Update `file` from todoist account. If no file is provided the default is 'TODO.txt'
    sync  <file>: Sync `file` with todoist account. If no file is provided the default is 'TODO.txt'
  SUBCOMMAND:
    -acc <file>: Choose todist account from cutstom .json `file`. Default is account.tobedone.json
    -p <project_name>: Choose todist project to work from. Defualt is `Inbox`"""

if __name__ == '__main__':
    arguments = list(reversed(sys.argv[1:].copy()))
    op: Optional[OpType] = None
    custom: bool = False
    config_path = 'config.tobedone.json'
    config = False
    args_copy = arguments.copy()
    while len(args_copy) > 0:
        argument = args_copy.pop()
        if argument == '--config':
            if len(args_copy) > 0:
                config_path = args_copy.pop()
            if os.path.exists(config_path):
                config = True
            else:
                print(f'[ERROR] Couldn\'t find filepath `{config_path}` for config')
                print(USAGE)
                sys.exit(1)
    if config:
        print(f'[INFO] Loading config from file: `{config_path}`')
        account, path, op, p_name = load_config_from_json(config_path)
    else:
        account, path, op, p_name = load_config_from_args(arguments)
    print(f'[INFO] Running op `{OP_HUMAN_NAMES[op]}` on project `{p_name}` with file `{path}`')
    succeeded: bool = False
    if op == OpType.PUSH:
        succeeded = update_todist_from_file(account, path, p_name)
    elif op == OpType.PULL:
        succeeded = update_file_from_todoist(account, path, p_name)
    elif op == OpType.SYNC:
        succeeded = sync_file_with_todoist(account, path, p_name)
    else:
        raise ValueError(f'Unknown operation {op}. This may be a bug in the parsing of the arguments')
    if succeeded:
        print('[SUCCESS] Succesfully finished execution')
    else:
        print('[ERROR] Execution failed, Try again')
