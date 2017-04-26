from .file import Kind as File
from .command import Kind as Command

class Kind(File, Command):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'test'
        self.default_action = 'execute'

