#!/usr/bin/env python

from data.create_tests import SEPARATOR

def main(pos, query_msd):
    results_file = 'results/%s_incorrect.txt' % pos
    test_file = 'tests/%s.tsv' % pos
    out_file = 'results/%s_incorrect.txt' % query_msd
    out = open(out_file, 'w')
    incorrect = set()
    for line in open(results_file):
        incorrect.add(line.strip())
    for line in open(test_file):
        form, analyses = line.strip().split('\t')
        for analysis in analyses.split(SEPARATOR):
            lemma, msd = analysis.split('-', 1)
            if query_msd in msd and form in incorrect:
                out.write('%s\n' % form)
    out.close()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('', '--pos',
            dest='pos',
            help='Part of speech to store',
            )
    parser.add_option('', '--msd',
            dest='msd',
            help='MSD to look for',
            )
    opts, args = parser.parse_args()
    main(opts.pos, opts.msd)

# vim: et sw=4 sts=4
