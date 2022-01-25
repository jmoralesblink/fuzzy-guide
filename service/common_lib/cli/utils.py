import logging
from typing import Union, Callable

from blink_logging_metrics.metrics import statsd

from common_lib.cli import prompt

_logger = logging.getLogger(__name__)


def command_tree(tree: dict[str, Union[dict, Callable]], statsd_prefix: str = None) -> None:
    """
    Present the user with a tree of options, with the leaf options triggering a callable command

    :param tree: a dictionary of options to select, with the key being the label displayed to the user, and the
    value being either a callable or another dictionary of sub-options.  The user will be presented with a list of all
    options at the current level, as well as a 'Back' option to move up a level, or return if already at the root level.
    :param statsd_prefix: if set, stats will be incremented whenever a callable is completed, or fails.  It will have
    the key '[statsd_prefix].command.completed' or '[statsd_prefix].command.failed'
    """
    # keep prompting the user to make a selection until they decide to exit
    options_stack = [("Select a section", tree)]
    while options_stack:
        # get the prompt and option list from the last item in the stack, and potentially add a "back" option
        option_prompt, options = options_stack[-1]
        option_names = list(options.keys())
        option_names.append("Back" if len(options_stack) > 1 else "Done")

        # prompt the user to make a selection
        selected_option_name = prompt.get_option(option_prompt, option_names)

        # handle the back option
        if selected_option_name == "Back":
            options_stack.pop()
            continue

        # handle the done option
        if selected_option_name == "Done":
            return

        # handle selecting an option that could be a command or a sub-list of more options
        selected_option = options[selected_option_name]
        if callable(selected_option):
            try:
                prompt.print_horizontal_rule()
                prompt.print(selected_option_name, style="title")
                prompt.print()
                selected_option()
                statsd.increment(f"{statsd_prefix}.command.completed", tags=[f"command:{selected_option_name}"])
                prompt.print_horizontal_rule()
            except Exception as ex:
                _logger.exception("Un-handled exception running ops_tool command")
                statsd.increment(f"{statsd_prefix}.command.failed", tags=[f"command:{selected_option_name}"])
        elif isinstance(selected_option, dict):
            options_stack.append((selected_option_name, selected_option))
        else:
            raise ValueError(f"Invalid option value: {selected_option}")

        prompt.print()
