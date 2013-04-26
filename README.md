slovene-morphological-analyzer
==============================

A finite state morphological analyzer for the Slovene language, written by
[Matt Gardner](http://www.cs.cmu.edu/~mg1/).

This analyzer is a fast, lightweight and easily extensible morphological
disambiguation tool written with [FOMA](https://code.google.com/p/foma/), an
open source reimplementation of Xerox's finite state tool, xfst.  The analyzer
disambiguates words into the [JOS](http://nl.ijs.si/jos/index-en.html)
morphosyntactic specifications
([MSDs](http://nl.ijs.si/jos/msd/html-en/index.html)).

The analyzer was built and tested using the
[Sloleks](http://www.slovenscina.eu/sloleks/opis) lexicon of Slovene language.
This code contains a script that processes Sloleks and outputs a set of FOMA
lexicon files for each part of speech, including whatever information is
necessary for a word's inflection (e.g., whether or not a final "e" is
fleeting, as in "pomemben" -> "pomembna" vs. "rumen" -> "rumena").  Each part
of speech then has rules for generating the regular and irregular morphology of
the language.

There are also scripts to test the output of analyzer against the MSDs
contained in Sloleks.  There are approximately 930,000 unique forms in Sloleks
(except for those marked as spelling errors, which we have so far ignored),
with an average of 3 possible MSD analyses for each form.  The test scripts can
test each part of speech individually, or all of them together, to see if the
set of analyses for each word matches what is found in Sloleks.  The system
currently has 100% recall on that test, and 98.8% precision.  That means that
for every word in Sloleks, this morphological analyzer produces a set of MSDs
that is a superset of analyses given in Sloleks, and for 98.8%, the sets match
exactly.  The remaining precision errors are mostly due to overprediction of
number or gender, where a proper noun only has a singular form, or a possessive
adjective only has a feminine form, or other similar issues.

100% recall was acheived by running a separate script that found remaining
errors and automatically generated lexicon override files for the forms that
were not correctly processed.  This was done after the rules were such that
about 96.5% of all forms were correctly processed - in lieu of encoding all of
the long tail of irregular morphology by hand, this was done automatically.

To get some idea of the coverage of this analyzer, a popular Slovene news site,
rtvslo.si, was scraped for textual content.  In the text of the most popular
articles, on average only between 2 and 5 percent of the tokens in the article
are not contained in the 930,000 forms in Sloleks.  The vast majority of these
tokens are sequences of digits (e.g., "2009") or proper names.  The analyzer
was thus improved to give guesses for unseen words---the number guesser works
well, though the proper name guesser currently vastly over-generates analyses.
But taking those two classes of tokens out of the unseen pool leaves less than
1% of the tokens unrecognized by this analyzer, and most of those are due to
processing errors (e.g., taking the period off of "oz.", which would otherwise
be recognized as an abbreviation, but is left as "oz", which is unrecognized,
or hyphenated words like "22-letna").  There is a script in this repository
that will perform this analysis on the current top articles on rtvslo.si.

The resulting analyzer is easily extensible in a number of ways.  If a newer,
improved version of Sloleks is released, the scripts here will easily process
it and update the generated lexicon files, assuming the format is the same.  If
a person wants to tackle some piece of the long tail of irregular morphology
that is currently left to automated overrides, it is easy to modify a few rules
in the files pertaining to that part of speech and run tests to see how much
the analyzer is improved.  And in implementing the number and proper name
guessers, some initial work was also given to guessing common feminine nouns,
which would cover the rare cases when a non-proper unseen word is encountered
in real text.  This is still very preliminary, but future work could expand the
unseen word guessing capabilities of the analyzer and add tests that compare
the guesses against the analyses given in Sloleks.  Because of the design of
the system, this should not be a lot of work for regular words; an addition of
four total lines of code in two files produced a guesser for feminine nouns
ending in "ost" that performs quite well.

# User Guide

### Processing Sloleks

From the `data/` directory, run `python create_lexica.py` and `python
create_tests.py`.  These commands will generate a number of files in the
`lexica/` and `tests/` directories.  These files are checked in to the
repository, so if you modify the Sloleks processing scripts, you can see the
difference it made by running `git diff`.

### Modifying lexical rules

For detailed information on `.lexc` and `.foma` files, look at FOMA's [Getting
Started guide](https://code.google.com/p/foma/wiki/GettingStarted).  Here I
will just explain the layout of the system.  Each part of speech has
(generally) 4 `.lexc` files in the `lexica/` directory.  Using verbs as an
example, these are:

* `verbs.lexc`, a file generated automatically by the `create_lexica.py`
  script,
* `verbs_rules.lexc`, a file written by hand that contains the basic
  morphological rules to inflect verbs,
* `verbs_overrides.lexc`, a file written by hand that contains irregular
  morphology for a small number of highly irregular words, and
* `verbs_auto_overrides.lexc`, a file generated automatically by running the
  `create_auto_overrides.py` script (described later).

There is also a single file containing regular expression rules that perform
stem changes and other complex morphological processes.  This file is
`foma/slovene.foma`.

### The `scripts/` directory

The `scripts/` directory contains four useful scripts, each of which is
described below.  All of these scripts should be run from the base directory,
with `python scripts/[script].py`.

* `make_bin.py`: This will combine all of the `.lexc` and `.foma` files, run
  them through FOMA, and produce a file called `slovene.bin`, which is suitable
  for use with `flookup`, or for loading into `foma`.  For more information on
  the use of those tools, see FOMA's user guide (linked above).
* `test.py`: This script first calls `make_bin.py`, then uses the resulting
  binary and the tests in the `tests/` directory to judge the accuracy of the
  analyzer.  For usage information run `python scripts/test.py --help`.  The
  results are shown in the `results/` directory.  The main results file is
  `results/[test]_stats.tsv`, which is suitable to be viewed with `sort`.
* `find_errors.py`: This will look through the error file for a particular test
  and select only those whose MSD matches some input.  This is useful, for
  example, if you want to see errors on only a particular kind of pronoun, even
  though you can only run tests on pronouns as a whole.
* `create_auto_overrides.py`: This file looks at the error file for a
  particular test, as well as the test file (originally generated from
  Sloleks), and produces an `*_auto_overrides.lexc`.  If you are working to
  improve the analyzer, you should run tests without the auto overrides (with
  the `--no-auto-overrides` option), then re-run this script to reproduce the
  (now hopefully smaller) `*_auto_overrides.lexc` file.

### The `scraping` directory

In this directory there is a script for scraping a few news articles from
rtvslo.si and running some tests to see what unseen words there are.  This
script is currently written to be run from the `scraping/` directory, not the
base directory.
