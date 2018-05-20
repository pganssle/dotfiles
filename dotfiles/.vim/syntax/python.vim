""" Add docstring support
syn region pythonDocstring  start=+^\s*"""+ end=+"""+ keepend excludenl
\ containedin=pythonString,String
\ contains=pythonEscape,@Spell,pythonDoctest,pythonDocTest2,pythonSpaceError
syn region pythonDocstring  start=+^\s*[uU]\?[rR]\?'''+ end=+'''+ keepend excludenl
\ containedin=pythonString, pythonUniString,pythonRawString
\ contains=pythonEscape,@Spell,pythonDoctest,pythonDocTest2,pythonSpaceError

