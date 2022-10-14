"""Netport integration with different databases."""
import re
import time
import datetime

from redis.client import Redis
from redis.exceptions import ResponseError
from redis import exceptions as redis_errors


class IDatabase:
    """General interface that describes the functionality needed for in a netport database."""

    def is_reserved(self, resource: str, value):
        """Check if the requested resource is already reserved."""
        raise NotImplementedError

    def reserve(self, client_ip: str, resource: str, value):
        """Reserve some resource for a client."""
        raise NotImplementedError

    def get_client_resources(
            self, client_ip: str, resource_regex: str = "*", value_regex: str = "*"
    ):
        """Get all the client resources that match the resource regex pattern."""
        raise NotImplementedError

    def release_resource(self, client_ip: str, resource: str, value):
        """Free the resource from its client."""
        raise NotImplementedError

    def release_client(self, client_ip: str):
        """Free the requested client from his resources."""
        raise NotImplementedError

    def get_all_clients(self):
        """Get all clients that posses resources in Netport."""
        raise NotImplementedError

    def get_all_resources(self):
        all_resources = {}
        for client in self.get_all_clients():
            client_resources = []
            for resource in self.get_client_resources(client):
                # Each resource might contain metadata about it in different databases. Therefore
                # to keep a similar usability of the different databases the `resource` is converted
                # to list before returning to the client.
                if type(resource) is list:
                    client_resources.append(resource)

                else:
                    client_resources.append([resource, ])

            all_resources[client] = client_resources

        return all_resources


class RedisDatabase(IDatabase):
    """Manages Netport's requests in a redis database.

    The data is saved and manages in Redis on a big hash table. Here is an example of one:

    | Client IP     | Resources                                 |
    | ------------- | ----------------------------------------- |
    | 192.168.0.128 | PORT:1234                                 |
    | 192.168.0.128 | PATH:/home/user/Downloads/version.tag.gz  |
    | 192.168.0.128 | PROCESS:ping 192.168.0.65                 |
    | 192.168.0.65  | PROCESS:bash /home/user/sniff_ping.sh     |

    In the given example we can see that there are 2 clients that currently use netport, client
    192.168.0.128 and 192.168.0.65. Also client 192.168.0.128 have requested 3 different resources
    compared to 192.168.0.65 who only requested 1 resource.
    """

    def __init__(self, host: str = "localhost", port: str = 6379, db_instance=0):
        try:
            self._db = Redis(host=host, port=int(port), db=db_instance)
            self._db.ping()

        except redis_errors.TimeoutError:
            raise TimeoutError("Couldn't connect to the Redis database")

    def is_reserved(self, resource: str, value):
        """Check if the requested resource is already reserved."""
        for client in self.get_all_clients():
            try:
                for _ in self.get_client_resources(client, resource, value):
                    return True
            except ResponseError as redis_error:
                if (
                        "WRONGTYPE Operation against a key holding the wrong kind of value"
                        in redis_error.args[0]
                ):
                    raise MemoryError(
                        "Seems like the Redis database have some keys that do not belong to "
                        f"Netport. Found the key '{client}'. Before continuing remove those types "
                        f"of keys."
                    ) from redis_error

                raise redis_error

        return False

    def reserve(self, client_ip: str, resource: str, value):
        """Reserve some resource for a client."""
        if self.is_reserved(resource, value):
            return False

        return (
                self._db.hset(
                    client_ip,
                    f"{resource}:{value}",
                    datetime.datetime.utcfromtimestamp(time.time()).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
                == 1
        )

    def get_client_resources(
            self, client_ip: str, resource_regex: str = "*", value_regex: str = "*"
    ):
        """Get all the client resources that match the resource regex pattern."""
        return self._db.hscan_iter(client_ip, match=f"{resource_regex}:{value_regex}")

    def release_resource(self, client_ip: str, resource: str, value):
        return self._db.hdel(client_ip, f"{resource}:{value}")

    def release_client(self, client_ip: str):
        return self._db.delete(client_ip) == 1

    def get_all_clients(self):
        return self._db.scan(cursor=0, match="*")[1]


class LocalDatabase(IDatabase):
    """Manages Netport's data in a pythonic dictionary without depending of any external tool.

    The data is saved inside a dictionary in which each key is a client containing a list of it's
    requested resources. The following is an example of how the data would look inside the
    LocalDatabase:

    {
        "192.168.0.128": [
            "PORT:1234",
            "PATH:/home/user/Downloads/version.tag.gz",
            "PROCESS:ping 192.168.0.65"
        ]
        "192.168.0.65" [
            "PROCESS:bash /home/user/sniff_ping.sh"
        ]
    }

    In the example above we can see the 2 clients, 192.168.0.128 and 192.168.0.65 with their
    resources.
    """

    def __init__(self):
        self._data = {}

    def is_reserved(self, resource: str, value):
        """Check if the requested resource is already reserved by some client."""
        record = rf"{resource}:{value}"
        for client in self._data.keys():
            if record in self._data[client]:
                return True

        return False

    def reserve(self, client_ip: str, resource: str, value):
        """Reserve some resource for a client."""
        if self.is_reserved(resource, value):
            return False

        record = f"{resource}:{value}"
        try:
            self._data[client_ip].append(record)
        except KeyError:
            self._data[client_ip] = [
                record,
            ]

        return True

    def get_client_resources(
            self, client_ip: str, resource_regex: str = r"(.)+", value_regex: str = r"(.)+"
    ):
        """Get all the client resources that match the resource regex pattern."""
        if client_ip not in list(self._data.keys()):
            return []

        matched_resources = []

        for record in self._data[client_ip]:
            if re.search(rf"{resource_regex}:{value_regex}", record):
                matched_resources.append(record)

        return matched_resources

    def release_resource(self, client_ip: str, resource: str, value):
        record = f"{resource}:{value}"
        if record in self._data[client_ip]:
            self._data[client_ip].remove(record)
            return True

        return False

    def release_client(self, client_ip: str):
        try:
            self._data.pop(client_ip)
            return True
        except KeyError:
            return False

    def get_all_clients(self):
        return list(self._data.keys())
