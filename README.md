# MRTracker

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/markbragin/mrtracker.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/markbragin/mrtracker/context:python)

MRTracker is a TUI time tracker.

## Installation

python3.10 is required.

You can install app using pip:
```bash
pip -m install mrtracker
```
or
```
python3.10 -m pip install mrtracker
```

## Usage

run the app:
```bash
mrtracker
```

make a backup:
```bash
mrtracker backup [-p path/to/backup]
```

restore:
```bash
mrtracker restore path/to/backup
```

export data to csv:
```bash
mrtracker csv [-p path/to/csv]
```

## Screenshot of the app

![mrtracker](./imgs/look.png "mrtracker")
