#!/usr/bin/env python

from collections import defaultdict
import gzip

SEPARATOR = ',-*-,'

def main(sloleks_file, test_dir):
    everything = defaultdict(list)
    proper_nouns = defaultdict(list)
    common_nouns = defaultdict(list)
    verbs = defaultdict(list)
    adjs = defaultdict(list)
    adverbs = defaultdict(list)
    pronouns = defaultdict(list)
    numerals = defaultdict(list)
    prepositions = defaultdict(list)
    conjunctions = defaultdict(list)
    particles = defaultdict(list)
    interjections = defaultdict(list)
    abbreviations = defaultdict(list)
    residuals = defaultdict(list)
    for line in gzip.open(sloleks_file):
        form, lemma, msd, freq, irreg = line.split('\t')
        if '*' in irreg: continue
        everything[form].append((lemma, msd))
        if msd.startswith('Np'):
            proper_nouns[form].append((lemma, msd))
        elif msd.startswith('Nc'):
            common_nouns[form].append((lemma, msd))
        elif msd[0] == 'A':
            adjs[form].append((lemma, msd))
        elif msd[0] == 'V':
            verbs[form].append((lemma, msd))
        elif msd[0] == 'R':
            adverbs[form].append((lemma, msd))
        elif msd[0] == 'P':
            pronouns[form].append((lemma, msd))
        elif msd[0] == 'M':
            numerals[form].append((lemma, msd))
        elif msd[0] == 'S':
            prepositions[form].append((lemma, msd))
        elif msd[0] == 'C':
            conjunctions[form].append((lemma, msd))
        elif msd[0] == 'Q':
            particles[form].append((lemma, msd))
        elif msd[0] == 'I':
            interjections[form].append((lemma, msd))
        elif msd[0] == 'Y':
            abbreviations[form].append((lemma, msd))
        elif msd[0] == 'X':
            residuals[form].append((lemma, msd))
    write_test_file(test_dir + 'common_nouns.tsv', common_nouns)
    write_test_file(test_dir + 'proper_nouns.tsv', proper_nouns)
    write_test_file(test_dir + 'verbs.tsv', verbs)
    write_test_file(test_dir + 'adjectives.tsv', adjs)
    write_test_file(test_dir + 'adverbs.tsv', adverbs)
    write_test_file(test_dir + 'pronouns.tsv', pronouns)
    write_test_file(test_dir + 'numerals.tsv', numerals)
    write_test_file(test_dir + 'prepositions.tsv', prepositions)
    write_test_file(test_dir + 'conjunctions.tsv', conjunctions)
    write_test_file(test_dir + 'particles.tsv', particles)
    write_test_file(test_dir + 'interjections.tsv', interjections)
    write_test_file(test_dir + 'abbreviations.tsv', abbreviations)
    write_test_file(test_dir + 'residuals.tsv', residuals)
    write_test_file(test_dir + 'everything.tsv', everything)


def write_test_file(filename, dictionary):
    tests = open(filename, 'w')
    keys = dictionary.keys()
    keys.sort()
    for key in keys:
        analyses = SEPARATOR.join(x[0]+'-'+x[1] for x in dictionary[key])
        tests.write('%s\t%s\n' % (key, analyses))


if __name__ == '__main__':
    main('sloleks-en.tbl.gz', '../tests/')

# vim: et sw=4 sts=4
