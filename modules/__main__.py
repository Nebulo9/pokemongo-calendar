if __name__ == "__main__":
    from .nebutil.log import LOGGER
    from . import EVENTS
    exit(0)
    print = LOGGER.info
    s = "BULBASAUR"
    print(s.partition('BA'))