import typer
from click_help_colors import HelpColorsCommand, HelpColorsGroup


class CustomHelpColorsGroup(HelpColorsGroup):
    """Overwrite help command to use colors."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"


class CustomHelpColorsCommand(HelpColorsCommand):
    """Overwrite help command to use colors."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"


class CustomTyper(typer.Typer):
    """Overwrite help to use colors."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            cls=CustomHelpColorsGroup,
            context_settings={"help_option_names": ["-h", "--help"]},
            **kwargs
        )

    def command(self, *args, **kwargs):
        """Overwrite help to use colors."""
        return super().command(
            *args,
            cls=CustomHelpColorsCommand,
            context_settings={"help_option_names": ["-h", "--help"]},
            **kwargs
        )
