from typing import Any

from pipeline import Pipeline, Supplier, Consumer, Mapper
import time


class NameGenerator(Supplier):
    def __init__(self):
        super().__init__()

    def supply(self) -> str:
        return "Name"


class Printer(Consumer):
    def __init__(self):
        super().__init__()

    def consume(self, value: Any):
        print(value)


class DelayMapper(Mapper):
    def __init__(self, delay: float):
        super().__init__()
        self.delay = delay

    def map(self, value):
        time.sleep(self.delay)
        return value

    def get_delay(self):
        return self.delay


class CountMapper(Mapper):
    def __init__(self):
        super().__init__()
        self.count = 0

    def map(self, value):
        self.count += 1
        return "[" + str(self.count) + "] " + value

    def get_count(self):
        return self.count


def run():
    example_pipe = Pipeline.builder() \
        .add(NameGenerator()) \
        .add(DelayMapper(0.5)) \
        .add(CountMapper()) \
        .add(Printer()) \
        .build()

    try:
        example_pipe.run()
    except KeyboardInterrupt:
        example_pipe.stop()


run()
