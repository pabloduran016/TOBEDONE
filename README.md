# PYDONE
Todoist sync aplication with python. Application to update data from todist and upload datat to todist using a txt

## Getting started:
First, install all the libraries:  
```bash
pip install -r requirements.txt
``` 
Then, create an account.pydone.json file with a key being "token":  
```json 
{"token": "Your API token"}
```
By default, the app while look for a file named `account.pydone.json` in the current directory. You can 
specify a custom file using the `-c` flag.  
You can get your API token in the Todoist app in Settings -> Integrations.


## Usage:
### FLAG
`--config` Use file named `config.pydone.json` to carry out execution` 
### Commands:
`push <file_path>` Update todoist account from `file`.  If no file is provided the default is 'TODO.txt'  
`pull <file_path>` Update `file` from todoist account.  If no file is provided the default is 'TODO.txt'  

### Subcommands:
`-c <file_path>` Choose todist account from cutstom .json `file` with the format determined before  
`-p <project_name>` Choose todist project to work from  

## References:
- [Todist API Docs](https://developer.todoist.com/sync/v8/#get-all-projects)  
- [Todoist API Module Docs](https://todoist-python.readthedocs.io/en/latest/)  
- [Todoist GitHub Repo](https://github.com/doist/todoist-python)  