from pycuid import CuidGenerator


if __name__ == "__main__":
    g = CuidGenerator()
    print g.cuid()
    print g.slug()

