from abc import ABC

from pipeline import Supplier, Consumer, Mapper, Pipeline


def main():
    pipe = Pipeline()
    pipe.run()


if __name__ == "__main__":
    main()
