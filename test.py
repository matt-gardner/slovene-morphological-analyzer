#!/usr/bin/env python

from __future__ import division

from collections import defaultdict
from subprocess import Popen, PIPE

from dirutil import create_dirs_and_open


def main(lexica, foma_file, test_files, results_dir, verbose):
    proc = Popen('cat %s > lexicon.lexc' % ' '.join(lexica), shell=True)
    proc.wait()
    proc = Popen(('foma', '-l', foma_file))
    proc.wait()
    for test in test_files:
        print 'Testing forms in', test
        cases = defaultdict(set)
        for line in open(test):
            form, analyses = line.strip().split('\t')
            analyses = analyses.split(',')
            for a in analyses:
                cases[form].add(a)

        seen = defaultdict(set)
        blocksize = 5000
        start = 0
        # This randomizes the order, which is good, if you want to just pick
        # the first N, or something
        keys = list(cases.keys())
        while start == 0 or start+blocksize < len(keys):
            if start % 20000 == 0:
                print start
            block = keys[start:start+blocksize]
            proc = Popen(('flookup', 'slovene.bin'), stdin=PIPE, stdout=PIPE)
            for form in block:
                proc.stdin.write('%s\n' % form)
            proc.stdin.close()
            for line in proc.stdout:
                if line.isspace(): continue
                form, analysis = line.strip().split('\t')
                seen[form].add(analysis_to_msd(analysis))
            proc.stdout.close()
            start += blocksize

        base = results_dir + test.split('/')[-1][:-4] + '_'
        incorrect_file = create_dirs_and_open(base + 'incorrect.txt')
        correct_file = create_dirs_and_open(base + 'correct.txt')
        overanalyzed_file = create_dirs_and_open(base + 'overanalyzed.txt')
        num_correct = 0
        num_incorrect = 0
        num_precise = 0
        num_both = 0
        incorrect_lemmas = set()
        unparseable = set()
        for form in cases:
            gold_set = cases[form]
            seen_set = seen[form]
            for analysis in seen_set:
                if '?' in analysis:
                    unparseable.add(form)
            intersection = gold_set.intersection(seen_set)
            recall = len(intersection) / len(gold_set)
            if len(seen_set) == 0:
                precision = 0.0
            else:
                precision = len(intersection) / len(seen_set)
            if recall != 1.0:
                if verbose:
                    print 'Form incorrect:', form
                    print '  Predicted:', ' '.join(x for x in seen_set)
                    print '  Gold:', ' '.join(x for x in gold_set)
                incorrect_file.write('%s\n' % form)
                num_incorrect += 1
                lemma = list(gold_set)[0].split('-')[0]
                incorrect_lemmas.add(lemma)
            else:
                correct_file.write('%s\n' % form)
                num_correct += 1
            if precision == 1.0:
                num_precise += 1
            elif precision != 0.0:
                overanalyzed_file.write('%s\n' % form)
            if precision == 1.0 and recall == 1.0:
                num_both += 1
        incorrect_file.close()
        correct_file.close()
        overanalyzed_file.close()
        total = len(cases)
        print 'Forms tested:', total
        print 'Percent with 100% recall:', num_correct / total
        print 'Percent with 100% precision:', num_precise / total
        print 'Percent with both:', num_both / total
        print 'Percent unparseable:', len(unparseable) / total
        incorrect_lemma_file = open(base + 'incorrect_lemmas.txt', 'w')
        for lemma in incorrect_lemmas:
            incorrect_lemma_file.write('%s\n' % lemma)
        incorrect_lemma_file.close()
        unparseable_file = open(base + 'unparseable.txt', 'w')
        for form in unparseable:
            unparseable_file.write('%s\n' % form)
        unparseable_file.close()


def analysis_to_msd(analysis):
    # The order of these is important.  Some symbols are prefixes of other
    # symbols, so the longer symbols must be placed first.  I'm grouping them
    # by phenomenon, so hopefully it will be easier to spot.
    replacements = [
            ('+General', 'g'), ('+Possessive', 's'), ('+Participle', 'p'),
            ('+Positive', 'p'), ('+Comparative', 'c'), ('+Superlative', 's'),
            ('+Animate', 'y'), ('+Inanimate', 'n'),
            ('+Definite', 'y'), ('+Indefinite', 'n'),
            ('+Main', 'm'), ('+Auxiliary', 'a'),
            ('+Perfective', 'e'), ('+Progressive', 'p'), ('+Biaspectual', 'b'),
            ('+First', '1'), ('+Second', '2'), ('+Third', '3'),
            ('+NoPerson', '-'), ('+NoAspect', '-'),
            ('+Infinitive', 'n'), ('+Supine', 'u'), ('+Present', 'r'),
            ('+Future', 'f'), ('+Conditional', 'c'), ('+Imperative', 'm'),
            ('+Negative', 'y'), ('+NotNegative', 'n'),
            ('+Nom', 'n'), ('+Gen', 'g'), ('+Dat', 'd'), ('+Acc', 'a'),
            ('+Loc', 'l'), ('+Ins', 'i'),
            ('+Sing', 's'), ('+Dual', 'd'), ('+Plural', 'p'),
            ('+Masc', 'm'), ('+Fem', 'f'), ('+Neut', 'n'),
            ('+A', '-A'),
            ('+V', '-V'),
            ('+N', '-Nc'), # Not general, yet; still need to handle propers
            ]
    msd = analysis
    for a, m in replacements:
        msd = msd.replace(a, m)
    return msd


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-s', '--small',
            help='Run small test instead of full test',
            dest='small',
            action='store_true')
    parser.add_option('-v', '--verbose',
            help='Show detailed error output',
            dest='verbose',
            action='store_true')
    opts, args = parser.parse_args()
    lexica = [
            'lexica/base.lexc',
            'lexica/adjs.lexc',
            'lexica/adj_rules.lexc',
            'lexica/common_fem_nouns.lexc',
            'lexica/common_masc_nouns.lexc',
            'lexica/common_neut_nouns.lexc',
            'lexica/noun_rules.lexc',
            'lexica/verbs.lexc',
            'lexica/verb_rules.lexc',
            ]
    foma_file = 'foma/slovene.foma'
    if opts.small:
        test_files = ['tests/adjs_small.tsv']
    else:
        test_files = [
                #'tests/common_fem_nouns.tsv',
                #'tests/common_masc_nouns.tsv',
                #'tests/common_neut_nouns.tsv',
                #'tests/adjs.tsv',
                'tests/verbs.tsv',
                ]
    results_dir = 'results/'
    main(lexica, foma_file, test_files, results_dir, opts.verbose)

# vim: et sw=4 sts=4
