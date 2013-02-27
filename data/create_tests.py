#!/usr/bin/env python

from collections import defaultdict
import gzip

def main(sloleks_file, test_dir):
    npms = defaultdict(list)
    npfs = defaultdict(list)
    npns = defaultdict(list)
    ncms = defaultdict(list)
    ncfs = defaultdict(list)
    ncns = defaultdict(list)
    verbs = defaultdict(list)
    adjs = defaultdict(list)
    others = defaultdict(list)
    for line in gzip.open(sloleks_file):
        form, lemma, msd, freq, irreg = line.split('\t')
        if '*' in irreg: continue
        if msd.startswith('Npm'):
            npms[form].append((lemma, msd))
        elif msd.startswith('Npf'):
            npfs[form].append((lemma, msd))
        elif msd.startswith('Npn'):
            npns[form].append((lemma, msd))
        elif msd.startswith('Ncm'):
            ncms[form].append((lemma, msd))
        elif msd.startswith('Ncf'):
            ncfs[form].append((lemma, msd))
        elif msd.startswith('Ncn'):
            ncns[form].append((lemma, msd))
        elif msd[0] == 'A':
            adjs[form].append((lemma, msd))
        elif msd[0] == 'V':
            verbs[form].append((lemma, msd))
        else:
            others[form].append((lemma, msd))
    write_test_file(test_dir + 'common_masc_nouns.tsv', ncms)
    write_test_file(test_dir + 'common_fem_nouns.tsv', ncfs)
    write_test_file(test_dir + 'common_neut_nouns.tsv', ncns)
    write_test_file(test_dir + 'proper_masc_nouns.tsv', npms)
    write_test_file(test_dir + 'proper_fem_nouns.tsv', npfs)
    write_test_file(test_dir + 'proper_neut_nouns.tsv', npns)
    write_test_file(test_dir + 'verbs.tsv', verbs)
    write_test_file(test_dir + 'adjs.tsv', adjs)
    write_test_file(test_dir + 'others.tsv', others)


def write_test_file(filename, dictionary):
    tests = open(filename, 'w')
    keys = dictionary.keys()
    keys.sort()
    for key in keys:
        analyses = ','.join(x[0]+'-'+x[1] for x in dictionary[key])
        tests.write('%s\t%s\n' % (key, analyses))


if __name__ == '__main__':
    main('sloleks-en.tbl', 'tests/')

# vim: et sw=4 sts=4
