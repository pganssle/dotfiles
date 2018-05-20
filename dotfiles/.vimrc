" Include Vundle
if filereadable(expand("~/.vim/.vimrc.bundles"))
    source ~/.vim/.vimrc.bundles
endif
if has('syntax') && !exists('g:syntax_on')
    syntax on
endif


" Color scheme
colorscheme pg-monokai

set termguicolors
let python_highlight_all = 1

"Information on the following settings can be found with
":help set
set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smarttab

set shiftwidth=4

set number
set ruler

set backspace=indent,eol,start

set pastetoggle=<F2>

" Window title
set title
let &titlestring = '[VIM] %t (%{expand("%:p:~:h")})'

" Backup
set backup
set backupdir=~/.vim/tmp/backup
set directory=~/.vim/tmp/swap

" Other
set encoding=utf-8
set wildignore+=*.pyc,*.pyo
set spell


if &enc =~ '^u\(tf\|cs\)'   " When running in a Unicode environment,
  set list                  " visually represent certain invisible characters:
  let s:arr = nr2char(9655) " using U+25B7 (▷) for an arrow, and
  let s:dot = nr2char(8901) " using U+22C5 (⋅) for a very light dot,
  " display tabs as an arrow followed by some dots (▷⋅⋅⋅⋅⋅⋅⋅),
  exe "set listchars=tab:"    . s:arr . s:dot
  " and display trailing and non-breaking spaces as U+22C5 (⋅).
  exe "set listchars+=trail:" . s:dot
  exe "set listchars+=nbsp:"  . s:dot
  " Also show an arrow+space (↪ ) at the beginning of any wrapped long lines?
  " I don't like this, but I probably would if I didn't use line numbers.
  " let &sbr=nr2char(8618).' '
  " Above taken from Matt Wozniski's .vimrc
endif

" Line guides
set cc=80,100

""""""""""""""
" Key bindings
"
" Make it so Ctrl-U and Ctrl-W in insert mode are recoverable
inoremap <c-u> <c-g>u<c-u>
inoremap <c-w> <c-g>u<c-w>

" F1 to see what syntax highlighting is applied
nm <silent> <F1> :echo "hi<" . synIDattr(synID(line("."),col("."),1),"name")
    \ . '> trans<' . synIDattr(synID(line("."),col("."),0),"name")
    \ . "> lo<" . synIDattr(synIDtrans(synID(line("."),col("."),1)),"name")
    \ . ">"<CR>

" Open undotree with F4
nnoremap <F4> :UndotreeToggle<cr>

" Set up org mode
if filereadable(expand("~/.org/org.vim"))
    source ~/.org/org.vim
endif

""""""""""""""
" Plugin settings

" ale

let g:ale_lint_on_text_changed = 0      " Lint only on save
let g:ale_lint_on_enter = 0
let g:ale_lint_on_save = 1

" Source local override file if one exists.
if filereadable(expand("~/.vimrc.local"))
    source ~/.vimrc.local
endif
