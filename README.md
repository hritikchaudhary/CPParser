# CP Parser

## Important Prerequisite
Go to Settings -> Package Settings -> CPParser -> Settings and add your directory paths.

Only Codeforces & Codechef are supported as of now I'll be adding support for other sites soon, please create an issue if you want to request support for a site.

This ST4 plugin functions as follows:

1. Accepts a problem URL like https://codeforces.com/problemset/problem/1900/D.
2. Parses the URL to extract the problem code.
3. Generates a new .cpp file using a predefined template.
4. Parses testcases on Codeforces & Codechef in CPPFastOlympicCoding format, so if you're using CPPFastOlympicCoding testcases will be automatically added.

### Usage
Upon installation, configuring settings (such as defining the default directory and snippets) is advised default path is ~/Documents/CPParser

1. Tools -> CP Parser -> New Problem
2. Command Palette -> search CP Parser: Parse New Problem

### Set Keybindings
You can access keybindings through Preferences > Key Bindings and add your Key Bindings like the following

```
{ "keys": ["ctrl+alt+x"], "command": "cp_problem" }
```

### Supported Websites (current)

1. Codeforces
2. Codechef
