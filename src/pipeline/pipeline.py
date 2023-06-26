import threading
from abc import ABC, abstractmethod
from typing import Any
from multiprocessing import Queue, Pool, Process
from concurrent.futures import ThreadPoolExecutor as ThreadPool

# from multiprocessing import Pool

MAX_QUEUE_BUFFER = 4


class PipelineComponent(ABC):
    def __init__(self):
        pass

    def abbreviate(self) -> str:
        return self.__class__.__name__

    def stop(self) -> None:
        pass


class Supplier(PipelineComponent):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def supply(self) -> Any:
        pass

    def abbreviate(self) -> str:
        return "SUP"


class Consumer(PipelineComponent):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def consume(self, obj: Any) -> None:
        pass

    def abbreviate(self) -> str:
        return "CON"


class Mapper(PipelineComponent):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def map(self, obj: Any) -> Any:
        pass

    def abbreviate(self) -> str:
        return "MAP"


class Pipeline:
    def __init__(self):
        self.__stages = []
        self.__working = False

    def __str__(self):
        message = ""
        for i in range(len(self.__stages)):
            stage = self.__stages[i]
            message += stage.component.abbreviate()
            if i < len(self.__stages) - 1:
                trailing_size = stage.trailing.get_size() if stage.trailing else 0
                message += " -[" + str(trailing_size) + "]-> "
        return message

    def add_component(self, component: PipelineComponent, simple_threading=False) -> None:
        stage = PipelineStage(component, simple_threading)
        if len(self.__stages) > 0:
            connector = PipelineConnector()
            before = self.__stages[-1]
            connector.between(before, stage)
        self.__stages.append(stage)

    def run(self):
        if self.__working:
            raise RuntimeError('Pipeline is already running')
        else:
            self.__working = True
        if len(self.__stages) < 2:
            raise RuntimeError('Pipeline should have at least two components')
        if not isinstance(self.__stages[0].component, Supplier):
            raise RuntimeError('First component should be a Supplier')
        if not isinstance(self.__stages[-1].component, Consumer):
            raise RuntimeError('Last component should be a Consumer')
        for component in self.__stages[1:-1]:
            if not isinstance(component.component, Mapper):
                raise RuntimeError('Middle components should be Mappers')
        for stage in self.__stages:
            print("Starting stage: " + stage.component.abbreviate())
            stage.run()

    def get_endpoint_sizes(self):
        return [stage.get_endpoint_sizes() for stage in self.__stages]

    def stop(self):
        for stage in self.__stages:
            stage.stop()

    @staticmethod
    def builder() -> 'PipelineBuilder':
        return PipelineBuilder()


class PipelineBuilder:
    def __init__(self):
        self.__pipeline = Pipeline()

    def add(self, component: PipelineComponent, simple_threading=False) -> 'PipelineBuilder':
        self.__pipeline.add_component(component, simple_threading)
        return self

    def build(self) -> Pipeline:
        return self.__pipeline


class PipelineStage:
    def __init__(self, component: PipelineComponent, use_simple_threading=False):
        self._leadingConnector = None
        self._trailingConnector = None
        self.component = component
        if isinstance(component, Supplier):
            self.__action = self.__supply
        elif isinstance(component, Consumer):
            self.__action = self.__consume
        elif isinstance(component, Mapper):
            self.__action = self.__map
        else:
            raise TypeError('Unknown component type')
        if use_simple_threading:
            self.__pool = threading.Thread(target=self.__loop)
        else:
            self.__pool = ThreadPool(1)
        self.__simple_threading = use_simple_threading

    @property
    def leading(self) -> 'PipelineConnector':
        return self._leadingConnector

    @leading.setter
    def leading(self, connector: 'PipelineConnector') -> None:
        self._leadingConnector = connector

    @property
    def trailing(self) -> 'PipelineConnector':
        return self._trailingConnector

    @trailing.setter
    def trailing(self, connector: 'PipelineConnector') -> None:
        self._trailingConnector = connector

    def run(self):
        if self.__simple_threading:
            self.__pool.start()
        else:
            self.__pool.submit(self.__loop)

    def __loop(self):
        while True:
            self.__action()

    def __supply(self) -> None:
        assert isinstance(self.component, Supplier)
        self._trailingConnector.put(self.component.supply())

    def __consume(self) -> None:
        assert isinstance(self.component, Consumer)
        self.component.consume(self._leadingConnector.get())

    def __map(self) -> None:
        assert isinstance(self.component, Mapper)
        obj = self._leadingConnector.get()
        self._trailingConnector.put(self.component.map(obj))

    def get_endpoint_sizes(self):
        leading = self._leadingConnector.get_size() if self._leadingConnector else "N/A"
        trailing = self._trailingConnector.get_size() if self._trailingConnector else "N/A"
        return [leading, trailing]

    def stop(self):
        self.component.stop()
        if self.__simple_threading:
            self.__pool.shutdown(wait=False)


class PipelineConnector:
    def __init__(self):
        self.__buffer = Queue(MAX_QUEUE_BUFFER)

    def between(self, first: PipelineStage, second: PipelineStage) -> None:
        first.trailing = self
        second.leading = self

    def put(self, obj: Any) -> None:
        self.__buffer.put(obj)

    def get(self) -> Any:
        return self.__buffer.get()

    def get_size(self) -> int:
        return self.__buffer.qsize()
