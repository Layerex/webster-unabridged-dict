#!/usr/bin/env python3

# import re

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from chm.chm import CHMFile
from chm.chmlib import chm_enumerate, CHM_ENUMERATE_NORMAL
from sys import argv, stderr

SUPERSCRIPT = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻", "(": "⁽", ")": "⁾", "=": "⁼", "/": "◌́", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ", "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "𐞥", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ꟲ", "D": "ᴰ", "E": "ᴱ", "F": "ꟳ", "G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ", "N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "ꟴ", "R": "ᴿ", "T": "ᵀ", "U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "Y": "𐞲"}
SUBSCRIPT =   {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉", "+": "₊", "-": "₋", "(": "₍", ")": "₎", "=": "₌", "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ", "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ", "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ"}

def format_entry(html: str):
    html = html.replace("\r\n", "\n")
    data = html.split("<DL>\n\n")[1].split("\n</DL>")[0]
    word, definition = data.removeprefix("<!--~--><DT>").split("<!--=-->")
    definition = definition.replace("<dd>", "")
    soup = BeautifulSoup(definition, "html.parser")

    def replace_tags(start: str, end: str, *args, f=None, **kwargs):
        for tag in soup.find_all(*args, **kwargs):
            if f:
                tag.contents[0] = NavigableString(f(tag.contents[0]))
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
    escape("35", "span", class_="col_indigo")

    formatted = str(soup)
    # tags = re.findall(r"<[^>]*>", formatted)
    definition = formatted.replace("&lt;", "<").replace("&gt;", ">").replace(" —", "\n—")
    # codes = re.findall(r"&[a-zA-Z];", formatted)
    
    alias = None
    word_parts = word.rstrip(".").split(", ")
    if len(word_parts) == 2:
        if len(word_parts[0]) == 1: # Single letter
            word = word_parts[0]
        elif word_parts[1].capitalize() in ("The", "A", "An", "'d", "L'", "La", "Il"):
            word = word_parts[0]
            definition = (f"{word_parts[1]} {word_parts[0]}\n" + definition).replace("\n", "\n ")

    print(f":{word}:{definition}")
    # if tags:
    #     print(tags, file=stderr)
    # if codes:
    #     print(codes, file=stderr)

def main():
    f = CHMFile()
    f.LoadCHM(argv[1])

    def enumerator(chm_file, ui, context):
        if len(ui.path) == 11 and ui.path.endswith(b".htm"):
            success, ui = f.ResolveObject(ui.path)
            assert success == 0
            _, content = f.RetrieveObject(ui)
            format_entry(content.decode())

    chm_enumerate(f.file, CHM_ENUMERATE_NORMAL, enumerator, None)

if __name__ == "__main__":
    main()
