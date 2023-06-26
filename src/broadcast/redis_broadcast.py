import time

from pipeline.pipeline import Consumer
import redis


class RedisBroadcast(Consumer):

    def __init__(self, redis_client: redis.Redis, channel: str):
        super().__init__()
        self.redis_client = redis_client
        self.channel = channel

    def consume(self, message):
        self.redis_client.publish(self.channel, message)


if __name__ == "__main__":
    client = redis.Redis(host='localhost', port=6379)

    from pipeline.pipeline import Supplier, Pipeline, PipelineComponent
    import json


    class TestSupplier(Supplier):

        def __init__(self):
            super().__init__()
            self.i = 0

        def supply(self):
            self.i += 0.1
            pos = {"x": -0.5, "y": 1.2, "z": 0.4}
            msg = json.dumps(pos)
            time.sleep(0.5)
            print(msg)
            return msg


    pipe = Pipeline.builder() \
        .add(TestSupplier()) \
        .add(RedisBroadcast(client, 'Ball')) \
        .build()

    pipe.run()
