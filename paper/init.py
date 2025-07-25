"""Set up the template to use your name and data."""
import pathlib
import sys
import logging


def main() -> int:
    """"""
    first = input("First name: ")
    last = input("Last name: ")
    year = input("Year of graduation: ")

    template_file_name = "NameStudentYear_Thesis.tex"
    new_file_name = f"{first}{last}{year}_Thesis.tex"

    # Rename main tex file to fit standard naming scheme
    thesis = pathlib.Path(template_file_name)
    try:
        thesis.rename(new_file_name)
    except FileExistsError:
        logging.fatal(f"{new_file_name} exists")
        return 1
    except FileNotFoundError:
        logging.fatal(f"{template_file_name} not found")
        return 1

    # Point all sections to newly named main file as parent to please IDEs
    for path in pathlib.Path("sections").iterdir():
        with path.open("rt", encoding="utf-8") as p:
            contents = p.read()
            replaced = contents.replace(template_file_name, new_file_name)
        with path.open("wt", encoding="utf-8") as p:
            p.write(replaced)

    # Update build system
    make_file = pathlib.Path("Makefile")
    with make_file.open("rt", encoding="utf-8") as p:
        contents = p.read()
        replaced = contents.replace("NameStudentYear_Thesis", f"{first}{last}{year}_Thesis")
    with make_file.open("wt", encoding="utf-8") as p:
        p.write(replaced)

    return 0


if __name__ == "__main__":
    sys.exit(main())
