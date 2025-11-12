from .._exceptions import AIMLAPIError

INSTRUCTIONS = """

AI/ML API error:

    missing `{library}`

This feature requires additional dependencies:

    $ pip install aimlapi[{extra}]

"""


def format_instructions(*, library: str, extra: str) -> str:
    return INSTRUCTIONS.format(library=library, extra=extra)


class MissingDependencyError(AIMLAPIError):
    pass
