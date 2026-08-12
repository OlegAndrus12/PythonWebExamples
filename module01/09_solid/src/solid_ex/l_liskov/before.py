import zlib


class Storage:
    def __init__(self, name):
        self.name = name
        self.files = {}

    def save(self, filename, data):
        self.files[filename] = data

    def read(self, filename):
        return self.files[filename]


class ReadOnlyStorage(Storage):
    def save(self, filename, data):
        raise PermissionError(f"{self.name} is read-only")


class CompressedStorage(Storage):
    def save(self, filename, data):
        self.files[filename] = zlib.compress(data.encode())


def backup(storages, filename, data):
    for storage in storages:
        storage.save(filename, data)
        print(f"saved to {storage.name}")


def verify(storages, filename, data):
    for storage in storages:
        status = "ok" if storage.read(filename) == data else "corrupted"
        print(f"{storage.name}: {status}")


if __name__ == "__main__":
    storages = [Storage("local"), CompressedStorage("zipped")]
    backup(storages, "db.dump", "orders data")
    verify(storages, "db.dump", "orders data")

    try:
        backup([Storage("s3"), ReadOnlyStorage("archive")], "db.dump", "orders data")
    except PermissionError as err:
        print(f"PermissionError: {err}")
