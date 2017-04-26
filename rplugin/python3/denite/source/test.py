from .base import Base
import os
import glob
import re

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'test'
        self.kind = 'test'
        self.current_directory = os.getcwd()

    def gather_candidates(self, context):
        candidates = []
        test_type = self.__get_test_type()
        test_folder_path = os.path.join(self.current_directory, test_type)
        rx = re.compile(f".*_{test_type}\..*$")
        for root, dirs, files in os.walk(test_folder_path):
            candidate = self.__build_candidate(root)
            candidates.append(candidate)

            for file in [file for file in files if rx.match(file)]:
                candidate = self.__build_candidate(os.path.join(root, file))
                candidates.append(candidate)

        return candidates

    def __get_test_type(self):
        if os.path.exists(os.path.join(self.current_directory, "spec")):
            return "spec"
        else:
            return "test"

    def __build_candidate(self, path):
        return {
            'word': path,
            'abbr': path.replace(self.current_directory, '').strip('/'),
            'action__path': path,
            'action__command': f"Denite -buffer-name=test -mode=normal test_run:{path}"
        }

