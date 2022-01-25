Supporting files for the ops_tool command.

This module is named with a _impl suffix, because if it matched the name of the command exactly, Django wouldn't be
able to find the command.

The management files are top-level modules for supporting the core features of the ops tool.  Every public function
in them should take no parameters, and be a self-contained user experience.  That means that it should handle all
UI for communicating with the user, and getting information from them.  Once the function returns, the core ops tool
will resume showing the main menu.
