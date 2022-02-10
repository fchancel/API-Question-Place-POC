#!/bin/sh

# Formnat anmd remove unused imports form all *.py files , excepting in ./venv,\
# using autopep8 formatter and pycln for finding unused import statements.

check_pip_package() {
    for package in $@; do
        if [ -z "$(pip list | grep $package)" ]; then
            echo "please install $package package"
            exit
        fi
    done
}

format() {
    for file in $(find . -path ./venv -prune -false -o -name '*.py'); do

        python3 ./venv/bin/pycln -q -a $file | grep "removed"

        AUTOPEP8_OUTPUT=$(python3 ./venv/bin/autopep8 --in-place --max-line-length 120 -v $file 2>&1 >/dev/null | grep "[1-9] issue")

        if [ -n "$AUTOPEP8_OUTPUT" ]; then
            echo "Format file $file : \n $AUTOPEP8_OUTPUT"
        fi

    done

}

check_pip_package autopep8 pycln

OUTPUT=$(format)

if [ -z "$OUTPUT" ]; then
    echo "Nothing to do !"
else
    echo "$OUTPUT"
fi
