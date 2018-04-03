" VIM color file
" Generated from theme pg-monokai

" Clear existing highlighting
hi clear

" Inform vim that the background is {self.background}
set background=dark
if version > 580
    if exists("syntax_on")
        syntax reset
    endif
endif

set t_Co=256

let g:colors_name="pg-monokai"
hi Normal guifg=#F8F8F2 guibg=#21222b gui=NONE ctermfg=255 ctermbg=235 cterm=NONE
hi Comment guifg=#ecec00 guibg=NONE gui=NONE ctermfg=226 ctermbg=NONE cterm=NONE
hi Constant guifg=#aabcc1 guibg=NONE gui=NONE ctermfg=250 ctermbg=NONE cterm=NONE
hi Cursor guifg=NONE guibg=#f8f8f0 gui=NONE ctermfg=NONE ctermbg=255 cterm=NONE
hi Error guifg=#F8F8F2 guibg=#ff0000 gui=NONE ctermfg=255 ctermbg=196 cterm=NONE
hi Function guifg=#38c120 guibg=NONE gui=NONE ctermfg=70 ctermbg=NONE cterm=NONE
hi String guifg=#f8c018 guibg=NONE gui=NONE ctermfg=214 ctermbg=NONE cterm=NONE
hi Number guifg=#3187f0 guibg=NONE gui=NONE ctermfg=69 ctermbg=NONE cterm=NONE
hi Identifier guifg=#aabcc1 guibg=NONE gui=NONE ctermfg=250 ctermbg=NONE cterm=NONE
hi Keyword guifg=#dc3434 guibg=NONE gui=NONE ctermfg=167 ctermbg=NONE cterm=NONE
hi Operator guifg=#dc3434 guibg=NONE gui=NONE ctermfg=167 ctermbg=NONE cterm=NONE
hi ColorColumn ctermbg=5 guibg=#444444
hi pythonStatement guifg=#dc3434 guibg=NONE gui=NONE ctermfg=167 ctermbg=NONE cterm=NONE
hi pythonRepeat guifg=#dc3434 guibg=NONE gui=NONE ctermfg=167 ctermbg=NONE cterm=NONE
hi pythonImport guifg=#dc3434 guibg=NONE gui=NONE ctermfg=167 ctermbg=NONE cterm=NONE
hi pythonException guifg=#dc3434 guibg=NONE gui=NONE ctermfg=167 ctermbg=NONE cterm=NONE
hi pythonDecorator guifg=#38c120 guibg=NONE gui=NONE ctermfg=70 ctermbg=NONE cterm=NONE
hi pythonError guifg=#5eb9c4 guibg=NONE gui=bold ctermfg=74 ctermbg=NONE cterm=bold
hi pythonExClass guifg=#5eb9c4 guibg=NONE gui=bold ctermfg=74 ctermbg=NONE cterm=bold
hi pythonNumber guifg=#3187f0 guibg=NONE gui=NONE ctermfg=69 ctermbg=NONE cterm=NONE
hi pythonHexNumber guifg=#3187f0 guibg=NONE gui=NONE ctermfg=69 ctermbg=NONE cterm=NONE
hi pythonOctNumber guifg=#3187f0 guibg=NONE gui=NONE ctermfg=69 ctermbg=NONE cterm=NONE
hi pythonBinNumber guifg=#3187f0 guibg=NONE gui=NONE ctermfg=69 ctermbg=NONE cterm=NONE
hi pythonFloat guifg=#3187f0 guibg=NONE gui=NONE ctermfg=69 ctermbg=NONE cterm=NONE
hi pythonBuiltinObj guifg=#5eb9c4 guibg=NONE gui=bold ctermfg=74 ctermbg=NONE cterm=bold
hi pythonBuiltinFunc guifg=#bcbcbc guibg=NONE gui=NONE ctermfg=250 ctermbg=NONE cterm=NONE


syn region pythonDocstring  start=+^\s*[uU]\?[rR]\?"""+ end=+"""+ keepend excludenl contains=pythonEscape,@Spell,pythonDoctest,pythonDocTest2,pythonSpaceError
syn region pythonDocstring  start=+^\s*[uU]\?[rR]\?'''+ end=+'''+ keepend excludenl contains=pythonEscape,@Spell,pythonDoctest,pythonDocTest2,pythonSpaceError

hi pythonDocstring guifg=#218B97 guibg=NONE gui=NONE ctermfg=25 ctermbg=NONE cterm=NONE
