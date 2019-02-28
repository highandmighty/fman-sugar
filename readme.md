### fman plugin

...

### fman settings

Add `Key Bindings.json` with this content:

``` json
[
	{ "keys": ["F2"], "command": "rename" },
	{ "keys": ["Cmd+N"], "command": "create_and_edit_file" },
	{ "keys": ["Cmd+R"], "command": "command_palette" },
	{ "keys": ["Cmd+G"], "command": "go_to" },
	{ "keys": ["Esc"], "command": "deselect" },
	{ "keys": ["Cmd+Left"], "command": "go_up" },
	{ "keys": ["Cmd+P"], "command": "reload_plugins" },
	{ "keys": ["Cmd+F5"], "command": "reload" },
	{ "keys": ["Cmd+F8"], "command": "archive" },
	{ "keys": ["Cmd+Right"], "command": "same_pane_right" }
]
```

Add `File Context Menu.json` with this content:

``` json
[
	{ "caption": "-", "id": "open" },
	{ "caption": "&Open Command Prompt here", "command": "terminal_here"},
	{ "caption": "Copy &full path", "command": "copy_paths_to_clipboard"},
	{ "caption": "Copy full path (&safe)", "command": "copy_safe_paths_to_clipboard"},
	{ "caption": "-", "id": "archive" },
	{ "caption": "&Unzip file", "command": "unzip_file"}
]
```
