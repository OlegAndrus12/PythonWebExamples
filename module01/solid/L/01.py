from pathlib import Path
from zipfile import ZipFile


class FileManager:
    def __init__(self, filename):
        self.path = Path(filename)

    def read(self, encoding="utf-8"):
        return self.path.read_text(encoding)

    def write(self, data, encoding="utf-8"):
        self.path.write_text(data, encoding)

class ZipFileManager(FileManager):
    def __init__(self, filename):
        self.path = Path(filename)
    
    def read(self, delimite="asdasd", encoding="utf-8"):
        return self.path.read_text(encoding)

    def compress(self):
        with ZipFile(self.path.with_suffix(".zip"), mode="w") as archive:
            archive.write(self.path)

    def decompress(self):
        with ZipFile(self.path.with_suffix(".zip"), mode="r") as archive:
            archive.extractall()

# 1
manager = FileManager("test.txt")
manager.read()

# 2
manager = ZipFileManager("test.txt")
manager.read()