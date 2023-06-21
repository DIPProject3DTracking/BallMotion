from typing import Any

from pipeline.pipeline import Supplier, Consumer, Mapper


class StereoSupplier(Supplier):
    def __init__(self, left_supplier: Supplier, right_supplier: Supplier):
        super().__init__()
        self.__left_supplier = left_supplier
        self.__right_supplier = right_supplier

    def supply(self) -> Any:
        return self.__left_supplier.supply(), self.__right_supplier.supply()


class StereoMapper(Mapper):
    def __init__(self, left_mapper: Mapper, right_mapper: Mapper):
        super().__init__()
        self.__left_mapper = left_mapper
        self.__right_mapper = right_mapper

    def map(self, obj: Any) -> Any:
        return self.__left_mapper.map(obj[0]), self.__right_mapper.map(obj[1])


class StereoConsumer(Consumer):
    def __init__(self, left_consumer: Consumer, right_consumer: Consumer):
        super().__init__()
        self.__left_consumer = left_consumer
        self.__right_consumer = right_consumer

    def consume(self, obj: Any) -> None:
        self.__left_consumer.consume(obj[0]), self.__right_consumer.consume(obj[1])

    def abbreviate(self) -> str:
        return "CON"
