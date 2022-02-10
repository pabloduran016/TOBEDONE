import os.path
# import time
import traceback
from dataclasses import dataclass
import sys
from typing import Optional, List, Tuple, Dict, NewType
from enum import auto, Enum
from todoist.api import TodoistAPI
from todoist.models import Section
import json
import datetime


FILE_PATH = 'TODO.txt'
Task = Dict[str, str]
DAT_FMT = '%Y-%m-%d:%H:%M:%S'
TaskId = NewType('TaskId', int)
SectionId = NewType('SectionId', int)

NEW_LINE = '\n'
CLOSING_QUOTES = '\'"`'
BACK_SLAH = '\\'


@dataclass
class TODO:
    content: str
    id: Optional[TaskId]
    cat: Optional[str] = None
    cat_id: Optional[SectionId] = None
    description: str = ''
    priority: int = 0


def _tasks_from_strs(api: TodoistAPI, project_id: int, tstrs: List[str]) -> Dict[str, Task]:
    tasks = {}
    for t in api.projects.get_data(project_id)['items']:
        if t['content'] in tstrs:
            tasks[t['content']] = t
    return tasks


def _tasks_from_ids(api: TodoistAPI, tstrs: List[TODO]) -> Dict[str, Task]:
    return {t.content: api.items.get_by_id(t.id) for t in tstrs}


@dataclass
class TodistAccount:
    token: str


def _set_api(acc: TodistAccount) -> TodoistAPI:
    api = TodoistAPI(acc.token)
    api.sync()
    return api


def _add_task(api: TodoistAPI, project_id: int, todo: TODO, sec_id: Optional[int], commit: bool = True):
    if todo.content.strip() == '':
        return
    print(f'[DEBUG] Adding TODO: {todo}')
    api.items.add(todo.content, description=todo.description, priority=todo.priority,
                  project_id=project_id, section_id=sec_id)
    if commit:
        api.commit()


def _modify_task(api: TodoistAPI, todo: TODO, commit: bool = True):
    if todo.content.strip() == '':
        return
    print(f'[DEBUG] Modifying TODO: {todo}')
    api.items.get_by_id(todo.id).update(content=todo.content, description=todo.description,
                                        priority=todo.priority)
    if commit:
        api.commit()


def _complete_task(api: TodoistAPI, task: Task, commit: bool = True):
    api.items.complete(task['id'], datetime.datetime.today().strftime('%Y-%m-%d'))
    if commit:
        api.commit()


def _get_section(api: TodoistAPI, cat: str, project_id: int) -> Section:
    secs = api.sections.all(lambda e: e['project_id'] == project_id)
    for sec in secs:
        if sec['name'] == cat:
            s = sec
            break
    else:
        s = api.sections.add(cat, project_id=project_id)
    return s


def _add_tasks(api: TodoistAPI, project_id: int, tasks: List[TODO], commit: bool = True):
    for t in tasks:
        if t.cat is not None:
            s = _get_section(api, t.cat, project_id)
            _add_task(api, project_id, t, s['id'], commit=False)
        else:
            _add_task(api, project_id, t, None, commit=False)
    if commit:
        api.commit()


def _modify_tasks(api: TodoistAPI, tasks: List[TODO], commit: bool = True):
    for t in tasks:
        assert t.id is not None
        _modify_task(api, t, commit=False)
    if commit:
        api.commit()


def _complete_tasks(api: TodoistAPI, _project_id: int, tasks: List[TODO], commit: bool = True):
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
        print(f'[ERROR] Couldn\'t find account path `{file_path}`. Try setting it with the `-acc` arg or use '
              f'`--config`')
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


def _find_cat(line: str) -> Tuple[str, Optional[str]]:  # line, cat
    """Find a category. Takes quotes into account"""
    c = [line]
    quoting = None
    for i, char in enumerate(line):
        if char in CLOSING_QUOTES:
            if char == quoting:
                quoting = None
            elif char is None:
                quoting = char
            continue
        if i != 0 and char == ':' and line[i - 1] and quoting is None and line[i - 1] != BACK_SLAH:
            c = [line[:i], line[i + 1:]]
            break
    cat: Optional[str]
    if len(c) > 1:
        cat = c[0].strip()
        line = ''.join(c[1:]).strip()
    else:
        cat = None
    return line, cat


def _parse_cont_id_from_line(line: str) -> TODO:
    r_line = line[::-1]  # reverse the line to strat looking from the traceback
    id_sub_identifier = '(id#'[::-1]  # reverse the sub string identifier aswell
    id_end_identifier = ')'[::-1]  # reverse the end identifier aswell
    end = r_line.find(id_end_identifier)
    if end < 0:
        line, cat = _find_cat(line)
        return TODO(line, None, cat)
    start = r_line.find(id_sub_identifier, end)
    if start < 0:
        line, cat = _find_cat(line)
        return TODO(line, None, cat)
    val = r_line[end + len(id_end_identifier):start][::-1]  # Don't forget to reverse the output as well
    if val.isnumeric():
        cont = (r_line[:end].strip() + ' ' + r_line[start + len(id_sub_identifier):].strip())[::-1].strip()
        # Try finding a category:
        cont, cat = _find_cat(cont)
        return TODO(cont, TaskId(int(val)), cat)
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
        crossed_tasks: List[TODO] = []
        todos: List[TODO] = []
        # n2 = time.time()
        current_tasks: List[TODO] = []
        for e in api.projects.get_data(project_id)['items']:
            current_tasks.append(TODO(e['content'], e['id'], None, e['description']))
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                li = 0
                current_todo: Optional[TODO] = None
                while li < len(lines):
                    raw_line = lines[li].strip()
                    if raw_line.startswith('x'):
                        cont = raw_line[1:].strip()
                        todo = _parse_cont_id_from_line(cont)
                        current_todo = todo
                        crossed_tasks.append(todo)
                    elif raw_line.startswith('-'):
                        cont = lines[li].strip()
                        priority = 0
                        while priority < len(cont) and cont[priority] == '-': priority += 1
                        assert 1 <= priority, f'Priority must be at least 1: got {priority}'
                        todo = _parse_cont_id_from_line(cont[priority:])
                        todo.priority = min(priority, 4)
                        todos.append(todo)
                        current_todo = todo
                    else:
                        if current_todo is None:
                            print(f'[WARNING] Invalid TODO. Didn\'t get `-` nor `x` at the beginning and is '
                                  f'not a description:\n\t{raw_line}', file=sys.stderr)
                        else:
                            current_todo.description += lines[li]
                            while (li + 1) < len(lines) and lines[li + 1][0] not in ['x', '-']:
                                line = lines[li + 1]
                                current_todo.description += line
                                li += 1
                            current_todo.description = current_todo.description.strip().strip('\n')
                    li += 1

        completed_tasks_id = {e['task_id'] for e in api.completed.get_all(project_id=project_id)['items']}
        modified_tasks: List[TODO] = []
        new_tasks: List[TODO] = []
        for todo in todos:
            print(todo)
            if todo.id in completed_tasks_id:
                continue
            elif todo.id is None or todo.id not in [t.id for t in current_tasks]:
                new_tasks.append(todo)
            elif todo.content not in [t.content for t in current_tasks]:
                modified_tasks.append(todo)
            elif todo.description not in [t.description for t in current_tasks]:
                modified_tasks.append(todo)
            elif todo.priority != api.items.get_by_id(todo.id)['priority']:
                modified_tasks.append(todo)


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
        tasks = [TODO(e['content'], e['id'], cat_id=e['section_id'], description=e['description'], priority=e['priority'])
                      for e in api.projects.get_data(project_id)['items']]
        with open(file_path, 'w') as f:
            lines: Dict[SectionId, Dict[int, List[str]]] = {}
            for todo in tasks:
                if todo.cat_id is not None:
                    s = api.sections.get_by_id(todo.cat_id)['name'] + ': '
                else:
                    s = ''

                if todo.cat_id not in lines:
                    lines[todo.cat_id] = {}
                if todo.priority not in lines[todo.cat_id]:
                    lines[todo.cat_id][todo.priority] = []
                lines[todo.cat_id][todo.priority].append((f'{"".join("-" for _ in range(todo.priority))} {s}{todo.content} (id#{todo.id})\n{todo.description}'
                                                          f'{NEW_LINE if todo.description != "" else ""}'))
            f.writelines([line for section in lines.values() for prior in reversed(sorted(section.keys())) for line in section[prior]])  # flatten out the dict
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
