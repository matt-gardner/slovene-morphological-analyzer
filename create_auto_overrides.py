#!/usr/bin/env python

from collections import defaultdict
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
        if msd[1] == 'g':
            analysis += '+General'
        if msd[2] == 'p':
            analysis += '+Positive'
        elif msd[2] == 'c':
            analysis += '+Comparative'
        elif msd[2] == 's':
            analysis += '+Superlative'
        return analysis
    if msd[0] == 'V':
        analysis += '+V'
        if msd[1] == 'a':
            print 'I thought these were all ok...'
            exit(-1)
        if msd[1] == 'm':
            analysis += '+Main'
        if msd[2] == 'p':
            analysis += '+Progressive'
        elif msd[2] == 'e':
            analysis += '+Perfective'
        elif msd[2] == 'b':
            analysis += '+Biaspectual'
        else:
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
        if msd[4] == '1':
            analysis += '+First'
        elif msd[4] == '2':
            analysis += '+Second'
        elif msd[4] == '3':
            analysis += '+Third'
        elif msd[4] == '-':
            analysis += '+NoPerson'
        if msd[5] == 's':
            analysis += '+Sing'
        elif msd[5] == 'd':
            analysis += '+Dual'
        elif msd[5] == 'p':
            analysis += '+Plural'
        if len(msd) == 6:
            return analysis
        if msd[6] == 'm':
            analysis += '+Masc'
        elif msd[6] == 'f':
            analysis += '+Fem'
        elif msd[6] == 'n':
            analysis += '+Neut'
        if len(msd) > 7:
            print 'MSD too long'
            exit(-1)
        return analysis



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
