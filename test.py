#!/usr/bin/env python

from __future__ import division

from collections import defaultdict
from subprocess import Popen, PIPE

from dirutil import create_dirs_and_open

from data.create_tests import SEPARATOR


def main(lexica, foma_file, test_files, override_files, results_dir, verbose):
    proc = Popen('cat %s > lexicon.lexc' % ' '.join(lexica), shell=True)
    proc.wait()
    proc = Popen('cat %s > overrides.lexc' % ' '.join(override_files),
            shell=True)
    proc.wait()
    proc = Popen(('foma', '-l', foma_file))
    proc.wait()
    stats = defaultdict(lambda: defaultdict(int))
    for test in test_files:
        print 'Testing forms in', test
        cases = defaultdict(set)
        for line in open(test):
            form, analyses = line.strip().split('\t')
            analyses = analyses.split(SEPARATOR)
            for a in analyses:
                cases[form].add(a)

        seen = defaultdict(set)
        blocksize = 5000
        start = 0
        # This randomizes the order, which is good, if you want to just pick
        # the first N, or something
        keys = list(cases.keys())
        while start < len(keys):
            if start % 20000 == 0:
                print start
            block = keys[start:start+blocksize]
            proc = Popen(('flookup', 'slovene.bin'), stdin=PIPE, stdout=PIPE)
            for form in block:
                proc.stdin.write('%s\n' % form)
            proc.stdin.close()
            for line in proc.stdout:
                if line.isspace(): continue
                try:
                    form, analysis = line.strip().split('\t')
                except ValueError:
                    print 'Bad line from stdout:', line
                    exit(-1)
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
            form_unparseable = False
            gold_set = cases[form]
            seen_set = seen[form]
            for analysis in seen_set:
                if '?' in analysis:
                    unparseable.add(form)
                    form_unparseable = True
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
                    print '  Recall:', recall
                incorrect_file.write('%s\n' % form)
                num_incorrect += 1
                lemma = list(gold_set)[0].split('-')[0]
                incorrect_lemmas.add(lemma)
            else:
                correct_file.write('%s\n' % form)
                num_correct += 1
            if precision == 1.0:
                num_precise += 1
            elif not form_unparseable:
                overanalyzed_file.write('%s\n' % form)
                if verbose:
                    print 'Form incorrect:', form
                    print '  Predicted:', ' '.join(x for x in seen_set)
                    print '  Gold:', ' '.join(x for x in gold_set)
                    print '  Precision:', precision
            if precision == 1.0 and recall == 1.0:
                num_both += 1
            gold_msds = set([x.split('-', 1)[1] for x in gold_set])
            seen_msds = set()
            for analysis in seen_set:
                if analysis == '+?': continue
                fields = analysis.split('-', 1)
                if len(fields) == 1:
                    print 'Weird analysis:', analysis
                lemma, msd = analysis.split('-', 1)
                seen_msds.add(msd)
            for msd in gold_msds:
                stats[msd]['seen'] += 1
                if msd not in seen_msds:
                    stats[msd]['missed'] += 1
                if form_unparseable:
                    stats[msd]['unparseable'] += 1
            for msd in seen_msds:
                stats[msd]['predicted'] += 1
                if msd not in gold_msds:
                    stats[msd]['overpredicted'] += 1
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
        stats_file = open(base + 'stats.tsv', 'w')
        headers = 'msd\t'
        headers += 'num_seen\t'
        headers += '%missed\tnum_missed\t'
        headers += '%unparseable\tnum_unparseable\t'
        headers += 'num_predicted\t'
        headers += '%overpredicted\tnum_overpredicted\n'
        stats_file.write(headers)
        for msd in stats:
            num_seen = stats[msd]['seen']
            if num_seen != 0:
                percent_missed = stats[msd]['missed'] / num_seen
                percent_unparseable = stats[msd]['unparseable'] / num_seen
            else:
                percent_missed = 0.0
                percent_unparseable = 0.0
            num_predicted = stats[msd]['predicted']
            if num_predicted != 0:
                percent_overpred = stats[msd]['overpredicted'] / num_predicted
            else:
                percent_overpred = 0.0
            stats_file.write('%10s\t%d\t%.2f\t%d\t%.2f\t%d\t%d\t%.2f\t%d\n'
                    % (msd,
                        num_seen,
                        percent_missed, stats[msd]['missed'],
                        percent_unparseable, stats[msd]['unparseable'],
                        num_predicted,
                        percent_overpred, stats[msd]['overpredicted'],
                        ))
    proc = Popen('rm -f lexicon.lexc', shell=True)
    proc.wait()
    proc = Popen('rm -f overrides.lexc', shell=True)
    proc.wait()


def analysis_to_msd(analysis):
    # The order of these is important.  Some symbols are prefixes of other
    # symbols, so the longer symbols must be placed first.  I'm grouping them
    # by phenomenon, so hopefully it will be easier to spot.
    replacements = [
            ('+Coordinating', 'c'), ('+Subordinating', 's'),
            ('+IndefinitePronoun', 'i'), ('+NegativePronoun', 'z'),
            ('+AdvParticiple', 'r'),
            ('+Cardinal', 'c'), ('+Ordinal', 'o'), ('+Pronominal', 'p'),
            ('+Special', 's'),
            ('+Common', 'c'), ('+Proper', 'p'),
            ('+Digit', 'd'), ('+Roman', 'r'), ('+Letter', 'l'),
            ('+General', 'g'), ('+Possessive', 's'), ('+Participle', 'p'),
            ('+Positive', 'p'), ('+Comparative', 'c'), ('+Superlative', 's'),
            ('+Personal', 'p'), ('+Demonstrative', 'd'), ('+Relative', 'r'),
            ('+Reflexive', 'x'), ('+Interrogative', 'q'),
            ('+Animate', 'y'), ('+Inanimate', 'n'),
            ('+Definite', 'y'), ('+Indefinite', 'n'),
            ('+Main', 'm'), ('+Auxiliary', 'a'),
            ('+Perfective', 'e'), ('+Progressive', 'p'), ('+Biaspectual', 'b'),
            ('+First', '1'), ('+Second', '2'), ('+Third', '3'),
            ('+NoPerson', '-'), ('+NoAspect', '-'), ('+NoNumber', '-'),
            ('+Infinitive', 'n'), ('+Supine', 'u'), ('+Present', 'r'),
            ('+Future', 'f'), ('+Conditional', 'c'), ('+Imperative', 'm'),
            ('+Negative', 'y'), ('+NotNegative', 'n'),
            ('+Nom', 'n'), ('+Gen', 'g'), ('+Dat', 'd'), ('+Acc', 'a'),
            ('+Loc', 'l'), ('+Ins', 'i'), ('+NoCase', '-'),
            ('+Sing', 's'), ('+Dual', 'd'), ('+Plural', 'p'),
            ('+Masc', 'm'), ('+Fem', 'f'), ('+Neut', 'n'), ('+NoGender', '-'),
            ('+Preposition', '-S'),
            ('+Conjunction', '-C'),
            ('+Interjection', '-I'),
            ('+Particle', '-Q'),
            ('+Pronoun', '-P'),
            ('+Abbreviation', '-Y'),
            ('+Adverb', '-R'),
            ('+Numeral', '-M'),
            ('+A', '-A'), ('+V', '-V'), ('+N', '-N'),
            ]
    # Some MSDs for pronouns are very difficult to replicate in finite state
    # machines without some more complicated post-processing.  For example,
    # 'moj' specifies that its owner is singular, but must do so before endings
    # get applied, and to match the order of the MSD, we have to shift things
    # around out here.
    shift_replace = [
            ('+OwnerSing', 's'), ('+OwnerDual', 'd'), ('+OwnerPlural', 'p'),
            ('+OwnerMasc', 'm'), ('+OwnerFem', 'f'), ('+OwnerNeut', 'n'),
            ('+Clitic', '--y'), ('+BoundClitic', '--b'),
            ]
    msd = analysis
    for a, m in replacements:
        msd = msd.replace(a, m)
    for a, m in shift_replace:
        if a in msd:
            msd = msd.replace(a, '')
            msd += m
    return msd


if __name__ == '__main__':
    parts_of_speech = [
            'abbreviations',
            'adjectives',
            'adverbs',
            'conjunctions',
            'interjections',
            'nouns',
            'numerals',
            'particles',
            'prepositions',
            'pronouns',
            'residuals',
            'verbs',
            ]
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('', '--small',
            help='Run small test',
            dest='small',
            action='store_true')
    parser.add_option('-v', '--verbose',
            help='Show detailed error output',
            dest='verbose',
            action='store_true')
    parser.add_option('', '--everything',
            help='Test everything together (note that this is different from '
            'specifying all other options individually)',
            dest='everything',
            action='store_true')
    for pos in parts_of_speech:
        parser.add_option('', '--%s' % pos,
                help='Test %s' % pos,
                dest='%s' % pos,
                action='store_true')
    opts, args = parser.parse_args()
    testcases = {}
    for pos in parts_of_speech:
        testcases[pos] = {'lexica': [
                    'lexica/base.lexc',
                    'lexica/%s.lexc' % pos,
                    'lexica/%s_rules.lexc' % pos,
                    ],
                'overrides': [
                    'lexica/base.lexc',
                    'lexica/%s_overrides.lexc' % pos,
                    'lexica/%s_rules.lexc' % pos,
                    ],
                'test_files': [
                    'tests/%s.tsv' % pos,
                ]}
    # We special case this one, to have more fine-grained tests
    testcases['nouns'] = {'lexica': [
            'lexica/base.lexc',
            'lexica/common_fem_nouns.lexc',
            'lexica/common_masc_nouns.lexc',
            'lexica/common_neut_nouns.lexc',
            'lexica/proper_fem_nouns.lexc',
            'lexica/proper_masc_nouns.lexc',
            'lexica/proper_neut_nouns.lexc',
            'lexica/nouns_rules.lexc',
            ],
        'overrides': [
            'lexica/nouns_overrides.lexc',
            'lexica/nouns_rules.lexc',
            ],
        'test_files': [
            'tests/common_nouns.tsv',
            'tests/proper_nouns.tsv',
        ]}
    # We also need to special case the pronouns and the numerals, to add
    # adjective rules to them
    testcases['pronouns']['lexica'].append('lexica/adjectives_rules.lexc')
    testcases['numerals']['lexica'].append('lexica/adjectives_rules.lexc')
    # Though it's a big obnoxious, this one just should be modified by hand if
    # you want to run a different small test.
    small = {'lexica': testcases['nouns']['lexica'],
        'overrides': [],
        'test_files': [
            'tests/nouns_small.tsv',
        ]}
    everything = {
        'test_files': [
            'tests/everything.tsv',
        ]}
    # This mess is because it's really important that lexica/base.lexc comes
    # first, because it defines the multicharacter symbols. If lexica/base.lexc
    # is not first, FOMA segfaults.
    lexica = set()
    overrides = set()
    for pos in parts_of_speech:
        for l in testcases[pos]['lexica']:
            if l != 'lexica/base.lexc':
                lexica.add(l)
        for o in testcases[pos]['overrides']:
            if l != 'lexica/base.lexc':
                overrides.add(o)
    lexica = list(lexica)
    lexica.sort()
    overrides = list(overrides)
    overrides.sort()
    everything['lexica'] = ['lexica/base.lexc']
    everything['lexica'].extend(lexica)
    everything['overrides'] = ['lexica/base.lexc']
    everything['overrides'].extend(overrides)

    foma_file = 'foma/slovene.foma'
    results_dir = 'results/'
    to_test = []
    if opts.small:
        to_test.append(small)
    if opts.everything:
        to_test.append(everything)
    for pos in parts_of_speech:
        if getattr(opts, pos):
            to_test.append(testcases[pos])
    if not to_test:
        print 'No tests specified.  Exiting.'
        exit(0)
    for test in to_test:
        main(test['lexica'], foma_file, test['test_files'], test['overrides'],
                results_dir, opts.verbose)

# vim: et sw=4 sts=4
