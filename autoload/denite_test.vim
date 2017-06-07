let s:Vital = vital#of('vital')
let s:String = s:Vital.import('Data.String')

function! denite_test#run_test() abort "{{{
  let filepath = expand("%")
  let test_file_regex = '\v.*_(spec|test)\.(rb|exs)$'

  if match(filepath, test_file_regex) == -1
    if denite_test#run_last_test() == 0
      exec ":TestList"
    endif
  else
    let test = denite_test#build_test(filepath, line('.'))
    let g:denite_test_last_command = denite_test#build_vim_command(test)
    exec g:denite_test_last_command
  endif
endfunction "}}}

function! denite_test#run_last_test() abort "{{{
  " update file before running tests
  exec ':wall'

  if exists('g:denite_test_last_command')
    exec g:denite_test_last_command
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

function! denite_test#build_vim_command(test_command) abort "{{{
  " update file before running tests
  exec ':wall'

  let shellcmd = s:String.replace(a:test_command, ' ', '\\ ')
  let deniteOptions = '-buffer-name=test -mode=normal'
  let run_cmd = ':Denite '.deniteOptions.' test_run:'.shellcmd
  return run_cmd
endfunction "}}}

