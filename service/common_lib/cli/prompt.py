"""Simple functions that support writing to and reading from the terminal"""
from typing import List, Union, Tuple, Any, Iterable, Type

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# standard colors that all prompts should use, instead of specifying custom ones
# color options: https://rich.readthedocs.io/en/latest/appendix/colors.html#appendix-colors
theme = Theme(
    {
        # status
        "info": "dim cyan",
        "success": "green",
        "warning": "yellow",
        "error": "italic red",
        # structure
        "title": "bold magenta",
        "heading": "bold orange4",
        "label": "sky_blue3",
        "prompt": "khaki3",
        "link": "blue underline",
    }
)
console = Console(theme=theme)


# shortcut functions
# these can be imported as single character, like h, allowing you to write the following: f"{h('heading:') value"


def wrap_heading(text: str) -> str:
    """Wrap text with the heading style, as a shortcut for embedding heading text in a string"""
    return f"[heading]{text}[/heading]"


def wrap_link(text: str) -> str:
    """Wrap text with the link style, as a shortcut for embedding link text in a string"""
    return f"[link]{text}[/link]"


# basic print functions


def print(text: str = "", style: str = "default", end="\n"):
    """
    Just like regular print(), but adds some simple highlighting features

    You can use a style by passing it into the style parameter, or on specific text by surrounding it with style
    markers, like "Please use [warning]caution[/warning] when proceeding.
    """
    console.print(text, style=style, end=end)


def print_warning(text: str = "", end="\n"):
    console.print(text, style="warning", end=end)


def print_error(text: str = "", end="\n"):
    console.print(text, style="error", end=end)


def print_success(text: str = "", end="\n"):
    console.print(text, style="success", end=end)


# specialty print functions


def print_columns(*values: str, style: str = "default"):
    """Print a list of values left-to-right, wrapping as needed, or lining up in even columns"""
    console.print(Columns(values), style=style)


def print_horizontal_rule(text: str = "", style: str = ""):
    console.rule(text, style=style)


def print_table_objects(objects: Iterable[Any], attr_names: Iterable[str]):
    """Print a table from a list of objects, and a list of the attributes to print"""
    table = Table(show_header=True, header_style="heading")
    table.box = box.SIMPLE_HEAD

    # setup columns
    for attr in attr_names:
        table.add_column(attr)

    # add data for every row
    for obj in objects:
        table.add_row(*[str(getattr(obj, a)) for a in attr_names])

    # display the table
    console.print(table)


def print_table_values(objects: Iterable[Any], col_names: Iterable[str]):
    """Print a table from a list of tuples/iterables, and a list of the column names"""
    pass


def print_key_value(name: str, text: str = "", separator: str = ": ", end="\n"):
    console.print(f"[label]{name}{separator}[/label]{text}", end=end)


def print_key_value_list(**kwargs):
    """
    Print a list of key/value pairs, one per line

    If you want to use keys that have spaces or other special characters, you can always convert a regular dict into
    kwargs, instead of typing them as actual parameters.
    Ex: prompt.print_key_value_list(**{"First Name": "Jeffrey", "Last Name": "Harmon", "Age": 38})
    :param kwargs:
    :return:
    """
    longest_key = max(len(k) for k in kwargs.keys())
    for key, value in kwargs.items():
        print_key_value(key.ljust(longest_key), value)


# functions for getting data from the user


def _get_type_value(prompt: str, type: Type, prompt_suffix: str = ": ", retry_on_error: bool = True):
    """
    Get input from a user, and convert it to the requested type, alerting the user if the value is not valid

    If the user enters an invalid value twice, an error will be raised.  This allows a user to back out of a prompt
    that might be triggering an un-wanted action.
    """
    response = console.input(f"[prompt]{prompt}{prompt_suffix}[/prompt]")

    try:
        return type(response)
    except ValueError:
        console.print(f"[error]Invalid integer[/error] '{response}'")
        if not retry_on_error:
            raise
        return _get_type_value(prompt, type, prompt_suffix, retry_on_error=False)


def get_bool(prompt: str, prompt_suffix: str = ": ") -> bool:
    response = console.input(f"[prompt]{prompt} \[y/n]{prompt_suffix}[/prompt]")

    return response.lower() == "y"


def get_int(prompt: str, prompt_suffix: str = ": ") -> int:
    return _get_type_value(prompt, int, prompt_suffix)


def get_float(prompt: str, prompt_suffix: str = ": ") -> float:
    return _get_type_value(prompt, float, prompt_suffix)


def get_password(prompt: str, prompt_suffix: str = ": ") -> str:
    return console.input(f"[prompt]{prompt}{prompt_suffix}[/prompt]", password=True)


def get_str(prompt: str, prompt_suffix: str = ": ") -> str:
    return console.input(f"[prompt]{prompt}{prompt_suffix}[/prompt]")


def get_option(prompt: str, options: List[Union[str, Tuple[str, Any]]]) -> Any:
    """
    Display a list of options for the user to select, and return the selected option

    :param prompt: Text to display before showing the options.
    :param options: A list of values to select from.  The value can be a single item, where it will have its string
    representation shown in the list, or a tuple, where the first item is the label to display, and the second is the
    value returned if the label is selected.
    :return: The Item selected
    """
    # needs to support adding constant options, such as back, that aren't part of the list
    console.print(prompt, style="prompt")
    option_map = {str(i): o for i, o in enumerate(options, start=1)}
    for key, value in option_map.items():
        label = str(value[0]) if type(value) is tuple else str(value)
        print_key_value(f"  {key}", label, separator=") ")
    response = console.input("[prompt]:[/prompt] ")

    selected_option = option_map.get(response)

    while selected_option is None:
        print_error("Invalid option selected: " + response)
        response = console.input("[prompt]:[/prompt] ")
        selected_option = option_map.get(response)

    return selected_option[1] if type(selected_option) is tuple else selected_option
