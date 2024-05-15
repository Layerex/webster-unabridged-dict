#!/usr/bin/env python3

# import re

from sys import argv, stderr

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from chm.chm import CHMFile
from chm.chmlib import chm_enumerate, CHM_ENUMERATE_NORMAL

SUPERSCRIPT = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻", "(": "⁽", ")": "⁾", "=": "⁼", "/": "◌́", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "𐞥", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ꟲ", "D": "ᴰ", "E": "ᴱ", "F": "ꟳ", "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ", "N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "ꟴ", "R": "ᴿ", "T": "ᵀ", "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "Y": "𐞲"}
SUBSCRIPT =   {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉", "+": "₊", "-": "₋", "(": "₍", ")": "₎", "=": "₌", "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ"}


def format_entry(html: str, html_format: bool = False) -> tuple[str, str]:
    html = html.replace("\r\n", "\n")
    data = html.split("<DL>\n\n")[1].split("\n</DL>")[0]
    word, definition = data.removeprefix("<!--~--><DT>").split("<!--=-->")
    soup = BeautifulSoup(definition, "html.parser")

    def replace_tags(start: str, end: str, *args, f=None, cb=None, **kwargs):
        for tag in soup.find_all(*args, **kwargs):
            if cb:
                cb(tag)
            if f:
                tag.contents[0] = NavigableString(f(tag.contents[0]))
            if not html_format:
                if start:
                    tag.contents.insert(0, NavigableString(start))
                if end:
                    tag.contents.append(NavigableString(end))
                tag.unwrap()

    def plain(*args, **kwargs):
        replace_tags("", "", *args, **kwargs)

    def prefix(start: str, *args, **kwargs):
        replace_tags(start, "", *args, **kwargs)

    def escape(e: str, *args, **kwargs):
        replace_tags(f"\033[{e}m", "\033[0m", *args, **kwargs)

    def replace_by_dict(d: dict, s: str, tag: str) -> str:
        ns = ""
        success = True
        for c in s:
            try:
                ns += d[c]
            except KeyError:
                success = False
                ns += c
        if not success: # Restore tag
            return f"[{tag}]{ns}[/{tag}]"
        return ns

    def sup(s: str) -> str:
        return replace_by_dict(SUPERSCRIPT, s, "sup")

    def sub(s: str) -> str:
        return replace_by_dict(SUBSCRIPT, s, "sub")

    alternate_words = []

    def alternate(tag: str):
        for word in tag.find("b").text.removesuffix(";").split(", "):
            alternate_words.append(word)

    escape("35", "span", class_="col_indigo", cb=alternate)
    if not html_format:
        plain("dd")
        plain("sup", f=sup)
        plain("sub", f=sub)
        plain("span", class_="m1")
        prefix(" ", "span", class_="m2")
        prefix(" " * 2, "span", class_="m3")
        prefix(" " * 3, "span", class_="m4")
        escape("1", "b")
        escape("3", "i")
        escape("3", "span", class_="p")
        escape("4", "span", class_="col_darkgray")
        escape("31", "span", class_="col_darkred")
        escape("33", "span", class_="col_brown")
        escape("34", "span", class_="col_blue")

    formatted = str(soup)
    if html_format:
        definition = """<style>.m1{margin-left: 0px;}
.m2{margin-left: 5px;}
.m3{margin-left: 10px;}
.m4{margin-left: 15px;}
.p{font-style: italic}
.col_darkred{color: darkred}
.col_darkgray{color: darkgray}
.col_brown{color: brown}
.col_blue{color: blue}
.col_indigo{color: indigo}</style>""" + formatted
    else:
        definition = formatted.replace("&lt;", "<").replace("&gt;", ">").replace(" —", "\n—")

    alias = None
    word_parts = word.rstrip(".").split(", ")
    if len(word_parts) == 2:
        if len(word_parts[0]) == 1: # Single letter
            word = word_parts[0]
        elif word_parts[1].capitalize() in ("The", "A", "An", "'d", "L'", "La", "Il"):
            word = word_parts[0]
            full_word = f"{word_parts[1]} {word_parts[0]}"
            if html_format:
                definition = f"<p>{full_word}</p>{definition}"
            else:
                definition = f"{full_word}\n{definition}".replace("\n", "\n ")

    yield [word], definition
    if alternate_words:
        if html_format:
            alternate_definition = f"<p>{word}</p>{definition}"
        else:
            alternate_definition = f"{word}\n{definition}"
        yield alternate_words, alternate_definition


def main():
    slob_format = len(argv) in (3, 4)
    if slob_format:
        import slob

    f = CHMFile()
    f.LoadCHM(argv[1])

    entries = []

    def enumerator(chm_file, ui, context):
        if len(ui.path) == 11 and ui.path.endswith(b".htm"):
            success, ui = f.ResolveObject(ui.path)
            assert success == 0
            _, content = f.RetrieveObject(ui)
            for word, definition in format_entry(content.decode(), html_format=slob_format):
                entries.append((word, definition))

    chm_enumerate(f.file, CHM_ENUMERATE_NORMAL, enumerator, None)

    if slob_format:
        with slob.create(argv[2]) as s:
            if len(argv) == 4:
                s.tag("label", argv[3])
            for words, definition in entries:
                s.add(definition.encode("utf-8"), *words, content_type="text/html; charset=utf-8")
    else:  # jargon file
        for words, definition in entries:
            for word in words:
                print(f":{word}:{definition}")


if __name__ == "__main__":
    main()
