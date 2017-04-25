from .base import Base
from time import localtime, strftime, time
from sys import maxsize
import os

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'rspec'
        self.kind = 'command'

    def gather_candidates(self, context):
        candidates = []
        test_type = self.__get_test_type()
        test_folder_path = os.path.join(os.getcwd(), test_type)
        subdirectories = [x[0] for x in os.walk(test_folder_path)]
        for subdirectory in subdirectories:
            candidate = {
                'word': subdirectory,
                'action__command': "echo 'hum'"
            }
            candidates.append(candidate)
        return candidates

    def __get_test_type(self):
        if os.path.exists(os.path.join(os.getcwd(), "spec")):
            return "spec"
        else:
            return "test"


