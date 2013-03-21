#!/usr/bin/env python

from collections import defaultdict
from data.create_tests import SEPARATOR
from test import parts_of_speech

def main(test_file, error_file, outfilename):
    cases = defaultdict(set)
    for line in open(test_file):
        form, analyses = line.strip().split('\t')
        analyses = analyses.split(SEPARATOR)
        for a in analyses:
            cases[form].add(a)
    forms = set()
    for line in open(error_file):
        forms.add(line.strip())
    lines = []
    for form in forms:
        for msd in cases[form]:
            analysis = msd_to_analysis(msd)
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
            to_run.append(testcases[pos])
    if not to_run:
        print 'No parts of speech specified.  Exiting.'
        exit(0)
    for pos in to_run:
        main('tests/%s.tsv' % pos, 'results/%s_incorrect.txt' % pos,
                'lexica/%s_auto_overrides.lexc' % pos)

# vim: et sw=4 sts=4
