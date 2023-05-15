from abc import ABC, abstractmethod
from typing import Any


class PipelineComponent(ABC):
    def __init__(self):
        pass


class Supplier(PipelineComponent):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def supply(self) -> Any:
        pass


class Consumer(PipelineComponent):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def consume(self, obj: Any) -> None:
        pass


class Mapper(PipelineComponent):
    def __init__(self, func):
        super().__init__()
        self.func = func

    @abstractmethod
    def map(self, obj: Any) -> Any:
        pass


class Pipeline:
    def __init__(self):
        self.stages = []

    def __str__(self):
        return ' -> '.join([str(stage) for stage in self.stages])

    def add_component(self, component: PipelineComponent) -> None:
        self.stages.append(component)

    # TODO: Multi-threading
    def run(self):
        obj = None
        for stage in self.stages:
            if isinstance(stage, Supplier):
                obj = stage.supply()
            elif isinstance(stage, Consumer):
                stage.consume(obj)
            elif isinstance(stage, Mapper):
                obj = stage.map(obj)
            else:
                raise TypeError('Unknown component type')
