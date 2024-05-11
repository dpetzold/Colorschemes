import argparse
import typing

from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class Highlight:
    name: str
    guifg: str
    guibg: typing.Optional[str]
    gui: typing.Optional[str]

    def print(self):
        style = self.guifg
        if self.guibg and self.gui:
            style = f"{self.guifg} {self.gui.replace(',', ' ')} on {self.guibg}"
        elif self.guibg:
            style = f"{self.guifg} {self.guibg}"

        console.print(self.name, style=style)


def parse_attr(attr):
    parsed = attr.split("=")[1].replace(",", " ")

    if parsed in ("bg", "none", "fg"):
        parsed = None
    return parsed


def parse_hi(line):

    split = line.split()
    if len(split) < 3:
        return

    # print(split)

    return Highlight(
        name=split[1],
        guifg=parse_attr(split[2]),
        guibg=parse_attr(split[3]) if len(split) > 3 else None,
        gui=parse_attr(split[4]) if len(split) > 4 else None,
    )


def parse_vim(file):

    for line in file.readlines():
        if line.startswith("hi"):
            highlight = parse_hi(line)
            if highlight:
                highlight.print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=argparse.FileType("r"), help="pass a filename")
    args = parser.parse_args()

    parse_vim(args.filename)


main()
