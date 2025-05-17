# mermaid-ink-cli

[mermaid.ink](https://github.com/jihchi/mermaid.ink) cli client, with command line arguments similar to [mermaid-cli / mmdc](https://github.com/mermaid-js/mermaid-cli)

## Usage

    py -3 mmdc_ink.py -i gantt.mmd -o gantt.svg
    py -3 mmdc_ink.py -i graph.mmd -o graph.svg

## Building Windows EXE binaries

    pip install pyinstaller
    pyinstaller --onefile mmdc_ink.py

## Pandoc filter

To use with Pandoc, check out https://github.com/timofurrer/pandoc-mermaid-filter
Follow pandoc-mermaid-filter instructions, to get a "binary" built (whether thats and executable python script under Linux, or a Microsoft Windows binary .exe).
Then override the Mermaid command line binary to the filter.

Either override for the current session, or single run.

### Windows

    REM change below to patch your path
    set MERMAID_BIN=C:\code\py\mermaid-ink-cli\dist\mmdc_ink.exe
    set MERMAID_BIN=dist\mmdc_ink.exe

### Linux / Unix

    export MERMAID_BIN=mmdc_ink

### Pandoc sample

    pandoc README.md -o sample.html --filter pandoc-mermaid


I've not had much success with other filters as per Timo's readme comment.
https://github.com/pandoc-ext/diagram partially works, svg's get exported but they are missing from the final html :-(

## Mermaid Example - Graph

```mermaid
graph LR;
    A-->B;
```
