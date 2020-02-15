import argparse

class Client:
    def __init__(self, name):
        self.name = name


if __name__ == '__main__':
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    arguments = parser.parse_args()

