from .base import Base
from os import getcwd
from os.path import exists
from denite.process import Process
from denite.util import parse_command, abspath

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'test_run'
        self.kind = 'command'

    def on_init(self, context):
        context['__proc'] = None
        context['__test_path'] = context['args'][0] if len(
            context['args']) > 0 else context['path']

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def gather_candidates(self, context):
        if context['__proc']:
            return self.__async_gather_candidates(
                context, context['async_timeout'])

        if not exists(context['__test_path']):
            return []

        args = self.__build_command(context)
        self.print_message(context, args)
        context['__proc'] = Process(args, context, context['path'])
        context['__current_candidates'] = []
        return self.__async_gather_candidates(context, 0.5)

    def __async_gather_candidates(self, context, timeout):
        outs, errs = context['__proc'].communicate(timeout=timeout)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None

        candidates = []
        for line in outs:
            candidate = self.__build_candidate(line)
            candidates.append(candidate)

        return candidates

    def __build_command(self, context):
        return ["cat", context["__test_path"]]

    def __build_candidate(self, line):
        return {
            'word': line,
            'action__command': "echo 'hum'"
        }

