# TOBEDONE
Todoist sync aplication with python. Application to update data from todist and upload datat to todist using a txt

## Getting started:
First, clone the repo or donwload it in which everway you prefer. In reality, the only files you need is the 
[main.py](main.py) and the [requirements.txt](requirements.txt)  
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
Specify a custom file using the `-acc` flag.  
For the `config.tobedone.json` file to be used, you have to add the `--config` flag which looks for 
`config.tobedone.json` in the current directory. You can add an argument to specify a path.  
You can get your API token in the Todoist app in Settings -> Integrations.
When ever you want to perform an action, just give  ommand to the [main.py](main.py) program.  

## Setting up an executable
If you prefer to run the app directly with an executable  
### Windows
First, create a `name_for_file.cmd` and write the following:  
```bash
PATH_TO_PYTHON_EXE PATH_TO_MAIN_PY --config PATH_TO_CONFIG_FILE
```  
In my experience, is better to use absolute paths to avoid any kinds of mistakes.  
Alternatively to using a config file you can specify the arguments in the file.  
Tu run it just type:  
```bash
PATH_TO_FILE.cmd
```  
You can even set it as a programmed task using windows tasks programmer or even make a desktop shortcut.  

## Linux
To make an executable in linux you have to create a .sh file and write.  
```bash
PATH_TO_PYTHON_EXE PATH_TO_MAIN_PY --config PATH_TO_CONFIG_FILE
```
In my experience, is better to use absolute paths to avoid any kinds of mistakes.  
Alternatively to using a config file you can specify the arguments in the file. 
Then, you will have to make it an executable by running:  
```bash
chmod +x filename.sh
```
Whenever you need to run it just type in the terminal: 
```bash
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

## Usage:
```bash
  USAGE: python main.py [OPTINAL FLAGS] <COMMAND> [ARGS] 
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

## References:
- [Todist API Docs](https://developer.todoist.com/sync/v8/#get-all-projects)  
- [Todoist API Module Docs](https://todoist-python.readthedocs.io/en/latest/)  
- [Todoist GitHub Repo](https://github.com/doist/todoist-python)  