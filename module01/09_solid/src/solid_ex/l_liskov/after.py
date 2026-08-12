import zlib


class ReadableStorage:
    def __init__(self, name):
        self.name = name
        self.files = {}

    def read(self, filename):
        return self.files[filename]


class WritableStorage(ReadableStorage):
    def save(self, filename, data):
        self.files[filename] = data


class CompressedStorage(WritableStorage):
    def save(self, filename, data):
        self.files[filename] = zlib.compress(data.encode())

    def read(self, filename):
        return zlib.decompress(self.files[filename]).decode()


def backup(storages: list[WritableStorage], filename, data):
    for storage in storages:
        storage.save(filename, data)
        print(f"saved to {storage.name}")


def verify(storages: list[ReadableStorage], filename, data):
    for storage in storages:
        status = "ok" if storage.read(filename) == data else "corrupted"
        print(f"{storage.name}: {status}")


if __name__ == "__main__":
    local = WritableStorage("local")
    zipped = CompressedStorage("zipped")
    archive = ReadableStorage("archive")

    backup([local, zipped], "db.dump", "orders data")
    verify([local, zipped], "db.dump", "orders data")
    print(f"archive has save(): {hasattr(archive, 'save')}")
