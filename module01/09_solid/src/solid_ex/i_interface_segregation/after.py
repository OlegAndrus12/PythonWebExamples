from abc import ABC, abstractmethod


class Printer(ABC):
    @abstractmethod
    def print(self, doc): ...


class Scanner(ABC):
    @abstractmethod
    def scan(self, doc): ...


class Fax(ABC):
    @abstractmethod
    def fax(self, doc): ...


class OfficeStation(Printer, Scanner, Fax):
    def print(self, doc):
        print(f"printing {doc}")

    def scan(self, doc):
        print(f"scanning {doc}")

    def fax(self, doc):
        print(f"faxing {doc}")


class CheapPrinter(Printer):
    def print(self, doc):
        print(f"printing {doc}")


def scan_documents(scanner: Scanner, docs):
    for doc in docs:
        scanner.scan(doc)


def scanners_in(fleet):
    return [device for device in fleet if isinstance(device, Scanner)]


if __name__ == "__main__":
    fleet = [OfficeStation(), CheapPrinter(), OfficeStation()]
    docs = ["contract.pdf", "invoice.pdf"]

    print(f"{len(scanners_in(fleet))} of {len(fleet)} devices can scan")
    for scanner in scanners_in(fleet):
        scan_documents(scanner, docs)
