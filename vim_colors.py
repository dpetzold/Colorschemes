import argparse
import typing
import yaml

from collections import defaultdict
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class Highlight:
    name: str
    fg: str
    bg: typing.Optional[str]
    attrs: typing.Optional[str]

    @property
    def style(self):
        style = None
        if self.fg and self.bg and self.attrs:
            style = f"{self.fg} {self.attrs} on {self.bg}"
        elif self.fg and self.bg:
            style = f"{self.fg} on {self.bg}"
        elif self.fg:
            style = self.fg
        return style

    @property
    def styled(self):
        if self.style:
            return f"[{self.style}]{self.name}[/{self.style}]"
        return self.name


@dataclass
class VimColors:
    def parse_attr(self, attr):
        return attr.split("=")[1].replace(",", " ")

    def parse_attr_ex(self, attr):
        parsed = self.parse_attr(attr)
        if parsed in ("bg", "none", "fg"):
            parsed = ""
        return parsed

    def parse_hi(self, line):

        print(line)

        split = line.split()
        if len(split) < 3:
            return

        # print(split)

        return Highlight(
            name=split[1],
            fg=self.parse_attr(split[2]),
            bg=self.parse_attr_ex(split[3]) if len(split) > 3 else None,
            attrs=self.parse_attr_ex(split[4]).replace(",", " ")
            if len(split) > 4
            else None,
        )

    def parse(self, file):
        return [
            self.parse_hi(line.lstrip())
            for line in file.readlines()
            if line.strip().startswith("hi")
        ]


@dataclass
class LVimColors:
    def parse_attrs(self, attr):
        if attr == "b":
            return "bold"
        if attr == "u":
            return "underline"

    def parse_hi(self, name, _attrs):
        (fg, bg, attrs) = None, None, None

        split = _attrs.split()

        if len(split) > 0:
            fg = split[0]
        if len(split) > 1:
            bg = split[1]
        if len(split) > 2:
            attrs = split[2]

        return Highlight(
            name=name,
            fg=self.palette.get(fg),
            bg=self.palette.get(bg),
            attrs=self.parse_attrs(attrs),
        )

    def parse(self, filename):
        contents = yaml.safe_load(open(filename))
        self.palette = contents["palette"]
        return [
            self.parse_hi(name, attrs) for name, attrs in contents["highlights"].items()
        ]


def print_table(files):
    combined = defaultdict(dict)
    for filename, highlights in files.items():
        for hi in highlights:
            if hi and hi.fg:
                combined[hi.name][filename] = hi

    table = Table()

    position = {
        "darkplus.yml": [3, 4],
        "molokai.vim": [1, 2],
    }

    row_num = 1
    for name, files in sorted(combined.items()):
        row = ["" for i in range(5)]
        row[0] = str(row_num)
        for filename, hi in files.items():
            postions = position[filename]
            for pos, hi in zip(postions, [hi.styled, hi.style]):
                row[pos] = hi
        table.add_row(*row)
        row_num += 1

    console.print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+", help="Pass the filenames to compare")
    args = parser.parse_args()

    highlights = {}

    for filename in args.filenames:

        if filename.endswith(".vim"):
            highlights[filename] = VimColors().parse(open(filename, "r"))
        elif filename.endswith(".yml"):
            highlights[filename] = LVimColors().parse(filename)

    print_table(highlights)


main()
