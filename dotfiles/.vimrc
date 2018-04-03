" Include Vundle
if filereadable(expand("~/.vim/.vimrc.bundles"))
    source ~/.vim/.vimrc.bundles
endif
if has('syntax') && !exists('g:syntax_on')
    syntax on
endif

" Color scheme
colorscheme pg-monokai

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

" Source local override file if one exists.
if filereadable(expand("~/.vimrc.local"))
    source ~/.vimrc.local
endif
