from argparse import ArgumentParser

from rich import print

from . import backup
from .config import generate_backup_name


def backup_handler(args) -> None:
    location = backup.create_backup(args.path)
    print(f"dump created at [yellow]{location}[/]")


def restore_handler(args) -> None:
    try:
        backup.restore_data(args.filename)
    except FileNotFoundError:
        print("[red]PROVIDE CORRECT PATH TO BACKUP FILE")
        exit(1)
    print("[green]Data has been restored")


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
    help=f"specify path. Defaults to './mrtracker_<datetime>.backup'",
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
