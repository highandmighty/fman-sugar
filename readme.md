### fman plugin

...

### fman settings

Add `Key Bindings.json` with this content:

``` json
[
	{ "keys": ["F2"], "command": "rename" },
	{ "keys": ["Ctrl+N"], "command": "create_and_edit_file" },
  { "keys": ["Alt+R"], "command": "command_palette" },
	{ "keys": ["Alt+G"], "command": "go_to" },
  { "keys": ["Esc"], "command": "deselect" },
  { "keys": ["Ctrl+Left"], "command": "go_up" },
	{ "keys": ["Alt+P"], "command": "reload_plugins" },
	{ "keys": ["Alt+F5"], "command": "reload" },
	{ "keys": ["Alt+F8"], "command": "archive" },
	{ "keys": ["Alt+Right"], "command": "same_pane_right" }
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
