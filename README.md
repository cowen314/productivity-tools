# productivity-tools

Tools to increase productivity / automate the boring stuff

## Setup

1. `python -m venv venv`
1. `source venv/Scripts/activate`
1. `pip install -r requirements.txt -r requirements-dev.txt`

## Updating requirements

Add new packages to requirments.txt, then install with `pip install -r requirements.txt`.

## Notes on Typer

Typer throws some weird errors if the argument types are not supported. Make sure that the types of the arguments specified by each command / function are supported. 

If you see

```
TypeError: sequence item 0: expected str instance, int found
```

you probably are using an unsupported argument type.

