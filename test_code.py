import subprocess
import re


def test_flake8():
    proc = subprocess.Popen("flake8 --exclude=docs".split(),
                            stdout=subprocess.PIPE)

    proc.wait()

    out = proc.stdout.read().decode()

    lines = [l.strip() for l in out.split("\n")if l]

    print(out)

    assert not bool(lines)


def test_pylint():

    proc = subprocess.Popen(("pylint --disable=relative-beyond-top-level,"
                             "too-few-public-methods,protected-access,"
                             "invalid-name,missing-docstring,"
                             "too-many-instance-attributes,too-many-branches,"
                             "no-member,fixme,import-error"
                             " cogs base utils").split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    proc.wait()

    out = proc.stdout.read().decode()

    print(out)

    last_line = [l for l in out.split("\n")if l][-1]

    m = re.match(r"Your code has been rated at 10\.00\/10", last_line.strip())

    assert m is not None


if __name__ == "__main__":
    test_flake8()
    print("Flake8 success!")

    test_pylint()
    print("Pylint success!")
