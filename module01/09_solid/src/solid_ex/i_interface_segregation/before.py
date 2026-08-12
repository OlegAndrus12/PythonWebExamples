from abc import ABC, abstractmethod


class MultiFunctionDevice(ABC):
    @abstractmethod
    def print(self, doc): ...

    @abstractmethod
    def scan(self, doc): ...

    @abstractmethod
    def fax(self, doc): ...


class OfficeStation(MultiFunctionDevice):
    def print(self, doc):
        print(f"printing {doc}")

    def scan(self, doc):
        print(f"scanning {doc}")

    def fax(self, doc):
        print(f"faxing {doc}")


class CheapPrinter(MultiFunctionDevice):
    def print(self, doc):
        print(f"printing {doc}")

    def scan(self, doc):
        raise NotImplementedError("no scanner")

    def fax(self, doc):
        raise NotImplementedError("no fax")


def scan_documents(device, docs):
    for doc in docs:
        device.scan(doc)


if __name__ == "__main__":
    docs = ["contract.pdf", "invoice.pdf"]
    scan_documents(OfficeStation(), docs)

    try:
        scan_documents(CheapPrinter(), docs)
    except NotImplementedError as err:
        print(f"NotImplementedError: {err}")
