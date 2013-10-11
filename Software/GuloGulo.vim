" Gulo's vim color file
" Learned from molokai
" Usable colors
" 0	Black
" 4	DarkBlue
" 2	DarkGreen
" 6	DarkCyan
" 1	DarkRed
" 5	DarkMagenta
" 3	Brown
" 7	LightGray
" b4	Blue
" b2	Green
" b6	Cyan
" b1	Red
" b5	Magenta
" b3	Yellow
" b7	White

" Clear previous colors
hi clear

" Clear syntax highlighting
if exists("syntax_on")
	syntax reset
endif

" Set the background
set background=dark

let colors_name="GuloGulo"

hi Normal	ctermbg=0	ctermfg=7

" Set Integer colors
hi Number	cterm=bold	ctermfg=5

" Set string between quotes
hi String	cterm=none	ctermfg=6

" Set if statement color
hi Conditional	cterm=none	ctermfg=3

" Set def, class, print, for, boolean
hi Function	cterm=bold	ctermfg=3

" Set parenthesis matching
hi MatchParen	cterm=bold	ctermbg=0	ctermfg=2

" Set "in" "and" in for if, while statements
hi Operator	cterm=bold	ctermfg=4

" Set import
hi PreProc	cterm=bold	ctermfg=4

" Set For, While
hi Repeat	cterm=none	ctermfg=4

" Set def and class
hi Statement	cterm=bold	ctermfg=4

" Set comment
hi Comment	cterm=none	ctermfg=1

" Set vim line number
hi LineNr	cterm=none	ctermfg=2

" Set vim response text for search
hi Search	cterm=none	ctermfg=1
