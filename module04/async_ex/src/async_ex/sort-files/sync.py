"""
Sort files based on extensions
"""
from time import time
from pathlib import Path
from shutil import copyfile

source = "picture"
output = "Backup/"

def read_folder(path: Path) -> None:
    for el in path.iterdir():
        if el.is_dir():
            read_folder(el)
        else:
            copy_file(el)


def copy_file(file: Path) -> None:
    pass

output_folder = Path(output)  # dist
start = time()
read_folder(Path(source))
print(f"Completed: {time() - start}")

