import sys


def main():
    if len(sys.argv) < 2:
        from .app import TimeTracker
        TimeTracker.run(title="MRTracker")
    else:
        from .arg_parser import parser
        args = parser.parse_args()
        args.func(args)


if __name__ == "__main__":
    main()
