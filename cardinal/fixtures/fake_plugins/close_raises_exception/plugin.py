class TestCloseRaisesExceptionPlugin(object):
    def close(self):
        raise Exception()


def setup():
    return TestCloseRaisesExceptionPlugin()
