from abc import ABC, abstractmethod
from typing import Any


class PipelineComponent(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class Supplier(PipelineComponent):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def supply(self) -> Any:
        pass


class Consumer(PipelineComponent):
    def __init__(self, name):
        super().__init__()

    @abstractmethod
    def consume(self, obj: Any) -> None:
        pass


class Mapper(Supplier, Consumer):
    def __init__(self, name, func):
        super().__init__(name)
        self.func = func

    @abstractmethod
    def supply(self) -> Any:
        pass

    @abstractmethod
    def consume(self, obj: Any) -> None:
        pass


class Pipeline:
    def __init__(self):
        self.stages = []

    def __str__(self):
        return ' -> '.join([str(stage) for stage in self.stages])

    def add_component(self, component: PipelineComponent) -> None:
        self.stages.append(component)
