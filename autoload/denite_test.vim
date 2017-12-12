let s:Vital = vital#of('vital')
let s:String = s:Vital.import('Data.String')
let s:Buffer = s:Vital.import('Vim.Buffer')
let s:FilePath = s:Vital.import('System.Filepath')

fun! denite_test#open_file_at_line(line) abort "{{{
  let rx = '\v#?\s*(.+):(\d+):?.*$'
  let sanitized_line = s:String.trim(a:line)
  let matches = matchlist(sanitized_line, rx)
  if matches != []
    exe 'vnew '.matches[1]
    call feedkeys(matches[2].'G')
  endif
endf " }}}

fun! denite_test#execute_command(test_command) abort "{{{
  " update files before running tests
  exec ':wall'

  new
  normal K
  nmap <buffer> q :q<CR>
  nmap <buffer> <enter> :call denite_test#open_file_at_line(getline('.'))<CR>
  call termopen(a:test_command)
  normal G
endf "}}}

function! denite_test#run_test() abort "{{{
  let filepath = expand("%")
  let test_file_regex = '\v.*_(spec|test)\.(rb|exs)$'

  if match(filepath, test_file_regex) == -1
    if denite_test#run_last_test() == 0
      exec ":TestList"
    endif
  else
    let test = denite_test#build_test(filepath, line('.'))
    let test_command = denite_test#build_vim_command(test)
    call denite_test#execute_command(test_command)
    let g:denite_test_last_command = test_command
  endif
endfunction "}}}

function! denite_test#run_last_test() abort "{{{
  if exists('g:denite_test_last_command')
    call denite_test#execute_command(g:denite_test_last_command)
    return 1
  endif

  return 0
endfunction "}}}

function! denite_test#build_test(test, line) abort "{{{
  if a:line > 1
    return a:test.':'.a:line
  else
    return a:test
  endif
endfunction "}}}

function! denite_test#full_path(path) abort "{{{
  let cwd = fnamemodify(getcwd(), 'p')
  return s:FilePath.join(cwd, a:path)
endfunction "}}}

function! denite_test#filereadable(path) abort "{{{
  let fullpath = denite_test#full_path(a:path)
  return filereadable(fullpath)
endfunction "}}}

function! denite_test#build_vim_command(test_command) abort "{{{
  let shellcmd = s:String.replace(a:test_command, ' ', '\\ ')

  if denite_test#filereadable('spec/spec_helper.rb')
    let runner = 'rspec'
    if executable('./bin/rspec')
      let runner = './bin/rspec'
    endif

    return [runner, '--no-profile', '--color', '--format', 'documentation', shellcmd]
  elseif denite_test#filereadable('mix.exs')
    return ["mix", "test", shellcmd]
  else
    ['echo', 'NOK']
  endif
endfunction "}}}

