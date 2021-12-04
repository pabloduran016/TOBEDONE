
# TOBEDONE
Todoist sync aplication with python. Application to update data from todist and upload datat to todist using a txt

You can create a .txt file and sync it with the TOdoist app. Any changes you make on the app will affect the .txt 
the oder way around. Currently, the actions supporte are:  
* Push: Change the Todist app according to the text file
* Pull: Fetch the current changes from Todoist 
* Sync: Make all the tasks from either places appear in both and eliminate [crossed out tasks](#completed-tasks)  

## Tasks
Taks are defined in the text file starting with `-`. Example: `- Add enemies to my game`. TOBEDONE doesn't take into 
account the amount of spaces surrounding `-` so that example will be the same as saying: `   -  Add enemies to my game`.  

### Completed tasks
Completed tasks are defined in the text file starting with `x`. Example: `x Add enemies to my game`. The same rule as 
before is applied to the completed tasks.  

### Edited tasks
You can edit a task by changing its content provided that you don't modify the id at the end of the task.
The textfile has priority in the editing of tasks btw  

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
You can even set it as a programmed task using windows tasks programmer or even make a desktop shortcut.  

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
