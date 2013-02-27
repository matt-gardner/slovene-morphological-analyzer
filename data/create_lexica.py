#!/usr/bin/env python

from collections import defaultdict
import gzip

def main(sloleks_file, lex_dir):
    npms = set()
    npfs = set()
    npns = set()
    ncms = set()
    ncfs = set()
    ncns = set()
    verbs = set()
    adjs = set()
    others = set()
    for line in gzip.open(sloleks_file):
        form, lemma, msd, freq, irreg = line.split('\t')
        if '*' in irreg: continue
        if msd.startswith('Npm'):
            npms.add(lemma)
        elif msd.startswith('Npf'):
            npfs.add(lemma)
        elif msd.startswith('Npn'):
            npns.add(lemma)
        elif msd.startswith('Ncm'):
            ncms.add(lemma)
        elif msd.startswith('Ncf'):
            ncfs.add(lemma)
        elif msd.startswith('Ncn'):
            ncns.add(lemma)
        elif msd[0] == 'A':
            adjs.add(lemma)
        elif msd[0] == 'V':
            verbs.add(lemma)
        else:
            others.add(lemma)
    write_lexicon(lex_dir+'common_masc_nouns.lexc', ncms, 'NounMasc', 'NMasc')
    write_feminine_nouns(ncfs, lex_dir)
    write_lexicon(lex_dir+'common_neut_nouns.lexc', ncns, 'NounNeut', 'NNeut')
    write_lexicon(lex_dir+'proper_masc_nouns.lexc', npms, 'ProperNounMasc',
            'NMasc')
    write_lexicon(lex_dir+'proper_fem_nouns.lexc', npfs, 'ProperNounFem',
            'NFem')
    write_lexicon(lex_dir+'proper_neut_nouns.lexc', npns, 'ProperNounNeut',
            'NNeut')
    write_lexicon(lex_dir+'verbs.lexc', verbs, 'Verb', 'Vinf')
    write_lexicon(lex_dir+'adjs.lexc', adjs, 'Adj', 'AdjInf')
    write_lexicon(lex_dir+'others.lexc', others, 'Other', 'OtherInf')


def write_feminine_nouns(lemmas, lex_dir):
    a_lemmas = set()
    ost_lemmas = set()
    ev_lemmas = set()
    other_lemmas = set()
    for l in lemmas:
        if l.endswith('a'):
            a_lemmas.add(l)
        elif l.endswith('ev'):
            ev_lemmas.add(l)
        elif l.endswith('ost'):
            ost_lemmas.add(l)
        else:
            other_lemmas.add(l)
    out = open(lex_dir + 'common_fem_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, a_lemmas, 'NounFemA', 'NFemA')
    write_lexicon_to_open_file(out, ev_lemmas, 'NounFemEv', 'NFemEv')
    write_lexicon_to_open_file(out, ost_lemmas.union(other_lemmas),
            'NounFemOst', 'NFemOst')


def write_lexicon(filename, lemmas, name, continuation):
    out = open(filename, 'w')
    write_lexicon_to_open_file(out, lemmas, name, continuation)
    out.close()


def write_lexicon_to_open_file(out, lemmas, name, continuation):
    out.write('LEXICON %s\n\n' % name)
    lemmas = list(lemmas)
    lemmas.sort()
    for l in lemmas:
        out.write('%s %s;\n' % (l, continuation))


if __name__ == '__main__':
    main('sloleks-en.tbl.gz', '../lexica/')

# vim: et sw=4 sts=4
