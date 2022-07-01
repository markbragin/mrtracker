from .app import TimeTracker


def main():
    TimeTracker.run(title="Time tracker", log="textual.log")

if __name__ == "__main__":
    main()
