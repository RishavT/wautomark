"""Database related things"""

import json
from threading import Lock
import functools


def locked(lock):
    """Returns a wrappable function which locks the given function"""

    def wrapper(func):

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                lock.acquire()
                return func(*args, **kwargs)
            finally:
                lock.release()
        return wrapped
    return wrapper


class Videos:
    """Filesystem JSON based db with threading lock"""

    def __init__(self, filepath="results.txt"):
        self.filepath = filepath
        self.idx_lock = Lock()
        self.get_lock = Lock()
        self.update_lock = Lock()
        self.idx = None
        self.load_idx()

    def load_idx(self):
        """Sets the initial video index from self.filepath"""
        self.idx = len(self.get_videos().keys()) + 1

    def get_videos(self):
        @locked(self.get_lock)
        def func():
            try:
                with open(self.filepath) as thefile:
                    return json.load(thefile)
            except Exception as e:
                return {}

        return func()

    def get_new_idx(self):
        """Returns a new idx. Thread locked"""

        @locked(self.idx_lock)
        def func():
            try:
                return self.idx
            finally:
                self.idx += 1

        return func()

    def update_videos(self, key, value):

        @locked(self.update_lock)
        def func():
            videos = self.get_videos()
            videos[key] = value
            with open(self.filepath, "w") as thefile:
                return json.dump(videos, thefile)
        return func()
