
# TOBEDONE
Have you ever wanted to sync up TODOs from your mobile phone to any device you want?  

Tobedone is a python app that allows you to sync up any text file with your todoist account.  

The only thing you need to do is install the todist account and set up a config file in any other device.

You can create a `.txt` file and sync it with the Todoist app. Any changes you make on the app will affect the `.txt`

## Operations

| Operation | Description                                                                                            |
|-----------|--------------------------------------------------------------------------------------------------------|
| **push**  | Change the Todist app according to the text file                                                       |
| **pull**  | Fetch the current changes from Todoist                                                                 |
| **sync**  | Make all the todos from either places appear in both and eliminate [completed TODOs](#completed-todos) |
## Features
- [x] TODO creation with sections, descritptions and crossed todos
- [x] Fixmee inspired priority mechanism
- [ ] Snitch inspired TODO finding in project files


## TODOs
Todos are defined in the text file starting with `-`. Example: `- Add enemies to my game`. TOBEDONE doesn't take into 
account the amount of spaces surrounding `-` so that example will be the same as saying: `   -  Add enemies to my game`.  

### Priority
The priority of a todo can go from 1 (not important) to 4 (super important). You define the priority of a TODO by the amount
of `-` before the TODO's title. Example: `- Add enemies to my game` has priority 1 and `--- Increase the amount of FPS (rn is 10)`
has priority 3.  
As always the `.txt` file has priority.

Todos are also ordered by priorities in the file 

### Descriptions

Descriptions can be added really easiliy. You can just start a new line below your TODO and whatever you type after the 
TODO that doesn't start with `-` or `x` will be part of this description. Remember that in `sync` mode teh `.txt` file has
priority.  
Example: 
```
- Add enemies to my game                                                              <- <title>
  I was thinking maybe something like octuposes that are really big and eat people    <- <description>
```

### Completed TODOs
Completed todos are defined in the text file starting with `x`. Example: `x Add enemies to my game`. The same rule as 
before is applied to the completed todos.  

### Edited todos
You can edit a todo by changing its content provided that you don't modify the id at the end of the todo.
The textfile has priority in the editing of todos btw  

## Sections  
A section is defined by the first colon `:` you can escape a colon by surrounding it by quotes or using `\`

## Getting started
First, clone the repo or download it however you prefer. In reality, the only files you need are 
[tobedone.py](tobedone.py) and [requirements.txt](requirements.txt)  
After that, install all the libraries using pip:  
```bash
pip install -r requirements.txt
``` 
Then, create an `account.tobedone.json` file with a key being "account_token":  
```json 
{"account_token": "Your API token"}
```
You can also use a `config.tobedone.json` file  
````json
{
  "account_token": "Your api token",
  "project": "Project",
  "action": "sync",
  "file_path": "TODO.txt"
}
````
By default, the app while look for a file named `account.tobedone.json` in the current directory. You can 
specify a custom file using the `-acc` flag.  
For the `config.tobedone.json` file to be used, you have to add the `--config` flag which looks for
`config.tobedone.json` in the current directory. You can add an argument to specify a path.  
You can get your API token in the Todoist app in Settings -> Integrations.  
When ever you want to perform an action, just give command to the [tobedone.py](tobedone.py) program.  

## Usage:
```bash
  USAGE: python tobedone.py [OPTINAL FLAGS] <COMMAND> [ARGS] 
    OPTIONAL FLAGS:
      --config <file>: Use file named config.tobedone.json or `file` if provided to carry out execution
    COMMAND:
      push <file>: Update todoist account from `file`. If no file is provided the default is 'TODO.txt'
      pull <file>: Update `file` from todoist account. If no file is provided the default is 'TODO.txt'
      sync  <file>: Sync `file` with todoist account. If no file is provided the default is 'TODO.txt'
    SUBCOMMAND:
      -acc <file>: Choose todist account from cutstom .json `file`. Default is account.tobedone.json
      -p <project_name>: Choose todist project to work from. Defualt is `Inbox`
```

## Setting up an executable
If you prefer to run the app directly with an executable  
### Windows
First, create a `name_for_file.cmd` and write the following:  
```bash
PATH_TO_PYTHON_EXE PATH_TO_MAIN_PY --config PATH_TO_CONFIG_FILE
```  
In my experience, is better to use absolute paths to avoid any kinds of mistakes.  
Alternatively to using a config file you can just specify the arguments.  

This will create a command window. If you prefer to not show it you can write instead a .vbs file
```vbs
Set oShell = CreateObject("Wscript.Shell")
oShell.Run "PATH_TO_PYTHON_EXE PATH_TO_MAIN_PY --config PATH_TO_CONFIG_FILE", 0, false
```

Tu run it just type:  
```console
PATH_TO_FILE.cmd
```  
You can even set it as a programmed todo using windows todos programmer or even make a desktop shortcut.  

### Linux
To make an executable in linux you have to create a .sh file and write.  
```bash
PATH_TO_PYTHON_EXE PATH_TO_MAIN_PY --config PATH_TO_CONFIG_FILE
```
In my experience, is better to use absolute paths to avoid any kinds of mistakes.  
Alternatively to using a config file you can just specify the arguments. 
Then, you will have to make it an executable by running:  
```console
chmod +x filename.sh
```
Whenever you need to run it just type in the terminal: 
```console
/PATH_TO_FILE.sh
```
Then you can create shortcuts or whatever.  
If you are an experienced Linux user, you have probaly heard about crontab. With it, you can schedule
this program to run on the back and update your todos. 
To schedule it to run every 30 minutes you have to type `crontab -e`, which will open the editor
and add the line 
```bash
*/30 * * * * /PATH_TO_FILE.sh
```

## References:
- [Todist API Docs](https://developer.todoist.com/sync/v8/#get-all-projects)  
- [Todoist API Module Docs](https://todoist-python.readthedocs.io/en/latest/)  
- [Todoist GitHub Repo](https://github.com/doist/todoist-python)  
- [Fixmee](https://github.com/rolandwalker/fixmee): inspired the priority mechanism  
- [Snitch](https://github.com/tsoding/snitch): inspired the find `TODO` in files mechanism
