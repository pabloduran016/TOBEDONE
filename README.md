# TOBEDONE
Todoist sync aplication with python. Application to update data from todist and upload datat to todist using a txt

## Getting started:
First, install all the libraries:  
```bash
pip install -r requirements.txt
``` 
Then, create an `account.tobedone.json` file with a key being "token":  
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
For the `config.tobedone.json` file ot be used, you have to add the `--config` flag
You can get your API token in the Todoist app in Settings -> Integrations.


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