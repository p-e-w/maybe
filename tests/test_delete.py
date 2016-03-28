from common import maybe


def test_delete_file(tmpdir):
    myfile = tmpdir.join("myfile")
    # File does not yet exist (will be created when written to)
    assert not myfile.check()
    myfile.write("mycontent")
    assert myfile.check()
    assert maybe("-l rm %s" % myfile) == ("delete %s" % myfile)
    # File still exists (was not deleted)
    assert myfile.check()
