"""
Backed by Redis
"""
from typing import TypeVar, Generic, Set, Final, Generator, Callable, Optional

from redis import Redis

from recommender.db_config import primary_redis_conn

T = TypeVar("T")
created_queues: Set[str] = set()


class MessageStream(Generic[T]):
    queue_name: Final[str]
    __redis_connection: Final[Redis]
    __serializer: Callable[[T], str]
    __deserializer: Optional[Callable[[str], T]]

    def __init__(
        self,
        queue_name: str,
        serializer: Callable[[T], str],
        deserializer: Optional[Callable[[str], T]] = None,
        redis_connection: Redis = primary_redis_conn,
    ):
        self.queue_name = queue_name
        self.__serializer = serializer
        self.__deserializer = deserializer
        self.__redis_connection = redis_connection

    def publish_message(self, message: T):
        message_as_string = self.__serializer(message)
        self.__redis_connection.publish(self.queue_name, message_as_string)

    def subscribe_to_raw(self) -> Generator[str, None, None]:
        subscription = self.__redis_connection.pubsub()
        subscription.subscribe(self.queue_name)
        for message in subscription.listen():
            if message["type"] != "data":
                continue
            yield message["data"]

    def subscribe(self) -> Generator[T, None, None]:
        for message_as_string in self.subscribe_to_raw():
            yield self.__deserializer(message_as_string)
