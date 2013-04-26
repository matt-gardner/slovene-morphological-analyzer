#!/usr/bin/env python

from collections import defaultdict
sys.path.append('.')
from data.create_tests import SEPARATOR
from test import parts_of_speech

def main(test_file, error_file, outfilename):
    msds = defaultdict(set)
    forms = defaultdict(set)
    for line in open(test_file):
        form, analyses = line.strip().split('\t')
        analyses = analyses.split(SEPARATOR)
        for msd in analyses:
            msds[form].add(msd)
            forms[msd].add(form)
    forms_with_errors = set()
    for line in open(error_file):
        forms_with_errors.add(line.strip())
    # We do this back-and-forth because FOMA's priority union operates on the
    # upper strings, or the MSDs.  So if we see an error on a lower string, or
    # surface form, and override the MSD for it, we'll have a problem if that
    # MSD has more than one possible surface form.  We have to get all of the
    # surface forms for each MSD we want to override, and put them all here.
    to_analyze = set()
    for form in forms_with_errors:
        to_analyze.update(msds[form])
    lines = []
    for msd in to_analyze:
        analysis = msd_to_analysis(msd)
        for form in forms[msd]:
            lines.append('%s:%s #;\n' % (analysis, form))
    lines.sort()
    out = open(outfilename, 'w')
    out.write('LEXICON Root\n\n');
    for line in lines:
        out.write(line)
    out.close()


def msd_to_analysis(msd):
    lemma, msd = msd.split('-', 1)
    analysis = lemma
    if msd[0] == 'R':
        analysis += '+Adverb'
        if msd[1] == 'r':
            analysis += '+Participle'
            return analysis
        elif msd[1] == 'g':
            analysis += '+General'
        analysis += get_degree(msd[2])
        return analysis
    elif msd[0] == 'V':
        analysis += '+V'
        if msd[1] == 'm':
            analysis += '+Main'
        elif msd[1] == 'a':
            print 'I thought these were all ok...'
            exit(-1)
        if msd[2] == 'p':
            analysis += '+Progressive'
        elif msd[2] == 'e':
            analysis += '+Perfective'
        elif msd[2] == 'b':
            analysis += '+Biaspectual'
        elif msd[2] == '-':
            analysis += '+NoAspect'
        if msd[3] == 'r':
            analysis += '+Present'
        elif msd[3] == 'm':
            analysis += '+Imperative'
        elif msd[3] == 'p':
            analysis += '+Participle'
        elif msd[3] == 'u':
            analysis += '+Supine'
            return analysis
        elif msd[3] == 'n':
            analysis += '+Infinitive'
            return analysis
        else:
            print 'Error'
            exit(-1)
        analysis += get_person(msd[4])
        analysis += get_numder(msd[5])
        if len(msd) == 6:
            return analysis
        analysis += get_gender(msd[6])
        if len(msd) > 7:
            print 'MSD too long'
            exit(-1)
        return analysis
    elif msd[0] == 'A':
        analysis += '+A'
        if msd[1] == 'g':
            analysis += '+General'
        elif msd[1] == 's':
            analysis += '+Possessive'
        elif msd[1] == 'p':
            analysis += '+Participle'
        analysis += get_degree(msd[2])
        analysis += get_gender(msd[3])
        analysis += get_number(msd[4])
        analysis += get_case(msd[5])
        if len(msd) == 6:
            return analysis
        analysis += get_negative(msd[6])
        return analysis
    elif msd[0] == 'N':
        analysis += '+N'
        if msd[1] == 'c':
            analysis += '+Common'
        elif msd[1] == 'p':
            analysis += '+Proper'
        analysis += get_gender(msd[2])
        analysis += get_number(msd[3])
        analysis += get_case(msd[4])
        if len(msd) == 5:
            return analysis
        analysis += get_animate(msd[5])
        return analysis


def get_gender(char):
    if char == 'm':
        return '+Masc'
    elif char == 'f':
        return '+Fem'
    elif char == 'n':
        return '+Neut'


def get_number(char):
    if char == 's':
        return '+Sing'
    elif char == 'd':
        return '+Dual'
    elif char == 'p':
        return '+Plural'


def get_degree(char):
    if char == 'p':
        return '+Positive'
    elif char == 'c':
        return '+Comparative'
    elif char == 's':
        return '+Superlative'


def get_person(char):
    if char == '1':
        return '+First'
    elif char == '2':
        return '+Second'
    elif char == '3':
        return '+Third'
    elif char == '-':
        return '+NoPerson'


def get_case(char):
    if char == 'n':
        return '+Nom'
    elif char == 'g':
        return '+Gen'
    elif char == 'd':
        return '+Dat'
    elif char == 'a':
        return '+Acc'
    elif char == 'l':
        return '+Loc'
    elif char == 'i':
        return '+Ins'


def get_negative(char):
    if char == 'y':
        return '+Negative'
    elif char == 'n':
        return '+NotNegative'


def get_animate(char):
    if char == 'y':
        return '+Animate'
    elif char == 'n':
        return '+Inanimate'


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    poses = parts_of_speech
    poses.remove('nouns')
    poses.append('common_nouns')
    poses.append('proper_nouns')
    for pos in poses:
        parser.add_option('', '--%s' % pos,
                help='Test %s' % pos,
                dest='%s' % pos,
                action='store_true')
    opts, args = parser.parse_args()
    to_run = []
    for pos in poses:
        if getattr(opts, pos):
            to_run.append(pos)
    if not to_run:
        print 'No parts of speech specified.  Exiting.'
        exit(0)
    for pos in to_run:
        main('tests/%s.tsv' % pos, 'results/%s_incorrect.txt' % pos,
                'lexica/%s_auto_overrides.lexc' % pos)

# vim: et sw=4 sts=4
