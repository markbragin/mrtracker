from .app import MyApp


def main():
    MyApp.run(title="Time tracker", log="textual.log")

if __name__ == "__main__":
    main()
