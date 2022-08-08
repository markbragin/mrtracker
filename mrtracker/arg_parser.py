from argparse import ArgumentParser

from rich import print

from . import backup
from .config import generate_backup_name, generate_csv_name


def backup_handler(args) -> None:
    try:
        location = backup.create_backup(args.path)
    except FileNotFoundError as e:
        print(e)
    except NotADirectoryError as e:
        print(e)
    else:
        print(f"Backup created at [yellow]{location}[/]")


def restore_handler(args) -> None:
    try:
        backup.restore_data(args.filename)
    except FileNotFoundError as e:
        print(e)
    else:
        print("[green]Data has been restored")


def csv_handler(args) -> None:
    try:
        location = backup.create_csv(args.path)
    except IsADirectoryError as e:
        print(e)
    except NotADirectoryError as e:
        print(e)
    else:
        print(f"csv vile created at [yellow]{location}[/]")


parser = ArgumentParser(
    prog="mrtracker",
    description="mrtracker - a TUI time tracker.",
)

commands_parser = parser.add_subparsers(title="commands")

backup_parser = commands_parser.add_parser(
    name="backup",
    help="create backup",
)
backup_parser.add_argument(
    "-p",
    "--path",
    dest="path",
    default=generate_backup_name(),
    help=f"specify path. Defaults to <current directory>",
)
backup_parser.set_defaults(func=backup_handler)

restore_parser = commands_parser.add_parser(
    name="restore",
    help="restore db from backup (rewrites all your current data) ",
)
restore_parser.add_argument(
    "filename",
    help="specify path to backup",
)
restore_parser.set_defaults(func=restore_handler)

csv_parser = commands_parser.add_parser(
    name="csv",
    help="export data to csv",
)
csv_parser.add_argument(
    "-p",
    "--path",
    dest="path",
    default=generate_csv_name(),
    help=f"specify path. Defaults to <current directory>",
)
csv_parser.set_defaults(func=csv_handler)
