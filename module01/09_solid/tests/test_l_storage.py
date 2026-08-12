import pytest

from solid_ex.l_liskov import after, before


def test_before_replica_breaks_code_written_for_the_base():
    storages = [before.Storage("local"), before.ReadOnlyStorage("archive")]
    with pytest.raises(PermissionError):
        before.backup(storages, "db.dump", "data")


def test_before_compressed_storage_breaks_the_read_contract():
    zipped = before.CompressedStorage("zipped")
    zipped.save("db.dump", "data")
    assert zipped.read("db.dump") != "data"


def test_after_backup_writes_to_every_writable_storage():
    storages = [after.WritableStorage("local"), after.WritableStorage("s3")]
    after.backup(storages, "db.dump", "data")
    assert all(s.read("db.dump") == "data" for s in storages)


def test_after_compressed_storage_keeps_the_read_contract():
    zipped = after.CompressedStorage("zipped")
    zipped.save("db.dump", "data")
    assert zipped.read("db.dump") == "data"


def test_after_readonly_storage_never_claims_save():
    assert not hasattr(after.ReadableStorage("archive"), "save")
