from .base import Base
from os import getcwd
from os.path import exists, join
from denite.process import Process
from denite.util import parse_command, abspath
from re import compile

COLORS = [
    '#6c6c6c', '#ff6666', '#66ff66', '#ffd30a',
    '#1e95fd', '#ff13ff', '#1bc8c8', '#c0c0c0',
    '#383838', '#ff4444', '#44ff44', '#ffb30a',
    '#6699ff', '#f820ff', '#4ae2e2', '#ffffff',
]

class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'test_run'
        self.kind = 'command'
        self.current_directory = getcwd()
        self.candidate_rx = compile('#?\s*(?P<file_path>.+):(?P<line_number>\d+):?.*$')

    def on_init(self, context):
        context['__proc'] = None
        context['__test_path'] = context['args'][0] if len(
            context['args']) > 0 else context['path']

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def highlight(self):
        highlight_table = {
            '0': ' cterm=NONE ctermfg=NONE ctermbg=NONE gui=NONE guifg=NONE guibg=NONE',
            '1': ' cterm=BOLD gui=BOLD',
            '3': ' cterm=ITALIC gui=ITALIC',
            '4': ' cterm=UNDERLINE gui=UNDERLINE',
            '7': ' cterm=REVERSE gui=REVERSE',
            '8': ' ctermfg=0 ctermbg=0 guifg=#000000 guibg=#000000',
            '9': ' gui=UNDERCURL',
            '21': ' cterm=UNDERLINE gui=UNDERLINE',
            '22': ' gui=NONE',
            '23': ' gui=NONE',
            '24': ' gui=NONE',
            '25': ' gui=NONE',
            '27': ' gui=NONE',
            '28': ' ctermfg=NONE ctermbg=NONE guifg=NONE guibg=NONE',
            '29': ' gui=NONE',
            '39': ' ctermfg=NONE guifg=NONE',
            '49': ' ctermbg=NONE guibg=NONE',
        }

        for color in range(30, 37):
            highlight_table[f"{color}"] = f" ctermfg={color-30} guifg={COLORS[color-30]}"

            for color2 in [1, 3, 4, 7]:
                highlight_table[f"{color2};{color}"] = highlight_table[f"{color2}"] + highlight_table[f"{color}"]

        for color in range(40, 47):
            highlight_table[f"{color}"] = f" ctermbg={color-40} guibg={COLORS[color-40]}"

            for color2 in range(30, 37):
                highlight_table[f"{color2};{color}"] = highlight_table[f"{color2}"] + highlight_table[f"{color}"]

        self.vim.command("syntax match DeniteSource_test_run_conceal contained conceal \"\\e\\[[0-9;]*m\" containedin=DeniteSource_test_run")
        self.vim.command("syntax match DeniteSource_test_run_conceal contained conceal \"\\e\\[?1h\" containedin=DeniteSource_test_run")
        self.vim.command("syntax match DeniteSource_test_run_ignore contained conceal \"\\e\\[?\\d[hl]\\|\\e=\\r\\|\\r\\|\\e>\" containedin=DeniteSource_test_run")

        for key, highlight in highlight_table.items():
            syntax_name = f"DeniteSource_test_run_color{key.replace(';', '_')}"
            syntax_command = f"start=+\\e\\[0\\?{key}m+ end=+\\ze\\e[\\[0*m]\\|$+ contains=DeniteSource_test_run_conceal containedin=DeniteSource_test_run oneline"

            self.vim.command(f"syntax region {syntax_name} {syntax_command}")
            self.vim.command(f"highlight {syntax_name} {highlight}")

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
        path = context['path']
        test_path = context['__test_path']

        if exists(join(path, "spec", "spec_helper.rb")):
            runner = './bin/rspec' if exists('./bin/rspec') else 'rspec'
            return [runner, '--no-profile', '--color', '--format', 'documentation', test_path]

        elif exists(join(path, "mix.exs")):
            return ["mix", "test", test_path]

        else:
            return ["cat", test_path]

    def __build_candidate(self, line):
        sanitized_line = line.strip()
        match = self.candidate_rx.match(sanitized_line)
        if match:
            file_path = match.group('file_path')
            if exists(join(self.current_directory, file_path)):
                return {
                    'word': line,
                    'kind': 'file',
                    'action__path': file_path,
                    'action__line': match.group('line_number')
                }

        return {
            'word': line,
            'kind': 'common'
        }

