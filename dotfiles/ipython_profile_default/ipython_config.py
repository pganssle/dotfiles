import platform
import IPython.core.release

IPYTHON_VERSION = IPython.core.release.version
PYTHON_IMPLEMENTATION = platform.python_implementation()
PYTHON_VERSION = platform.python_version()
PYTHON_BUILD = platform.python_build()

# Single line startup banner
# Switch to f-string when 3.6 is an implausible version to use
BANNER_TEMPLATE = (
    "IPython {IPYTHON_VERSION}, on {PYTHON_IMPLEMENTATION} "
    + "{PYTHON_VERSION} ({PYTHON_BUILD[0]}, {PYTHON_BUILD[1]})\n"
)

c.InteractiveShell.banner1 = BANNER_TEMPLATE.format(
    IPYTHON_VERSION=IPYTHON_VERSION,
    PYTHON_VERSION=PYTHON_VERSION,
    PYTHON_BUILD=PYTHON_BUILD,
    PYTHON_IMPLEMENTATION=PYTHON_IMPLEMENTATION,
)

# No separator  between output and next input prompt
c.InteractiveShell.separate_in = ""
c.TerminalInteractiveShell.confirm_exit = False
if hasattr(c.TerminalInteractiveShell, "autoformatter"):
    c.TerminalInteractiveShell.autoformatter = None

# Classic python REPL prompts (e.g. >>>, ...)
c.TerminalInteractiveShell.prompts_class = "IPython.terminal.prompts.ClassicPrompts"
