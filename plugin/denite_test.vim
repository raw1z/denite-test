command! TestRun call denite_test#run_test()
command! TestRunLast call denite_test#run_last_test()
command! TestList Denite -mode=normal test

if !exists("g:denite_test_map_keys")
  let g:denite_test_map_keys = 1
endif

if g:denite_test_map_keys
  silent! map <unique> <Leader>r :TestRun<CR>
  silent! map <unique> <Leader>R :TestList<CR>
  silent! map <unique> <Leader>l :TestRunLast<CR>
endif

