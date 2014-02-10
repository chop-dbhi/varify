import _setenv  # noqa


def main():
    pass


if __name__ == '__main__':
    import timeit
    print(timeit.timeit('main()', setup='from __main__ import main'))
