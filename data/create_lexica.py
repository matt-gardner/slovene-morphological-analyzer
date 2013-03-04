#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    prepositions = set()
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
            ncms.add((lemma, msd))
        elif msd.startswith('Ncf'):
            ncfs.add(lemma)
        elif msd.startswith('Ncn'):
            ncns.add(lemma)
        elif msd[0] == 'A':
            adjs.add(lemma)
        elif msd[0] == 'V':
            verbs.add((lemma, msd))
        elif msd[0] == 'S':
            prepositions.add((lemma, msd))
        else:
            others.add(lemma)
    write_masculine_nouns(ncms, lex_dir)
    write_feminine_nouns(ncfs, lex_dir)
    write_neuter_nouns(ncns, lex_dir)
    write_adjectives(adjs, lex_dir)
    write_verbs(verbs, lex_dir)
    write_prepositions(prepositions, lex_dir)
    write_lexicon(lex_dir+'proper_masc_nouns.lexc', npms, 'ProperNounMasc',
            'NMasc')
    write_lexicon(lex_dir+'proper_fem_nouns.lexc', npfs, 'ProperNounFem',
            'NFem')
    write_lexicon(lex_dir+'proper_neut_nouns.lexc', npns, 'ProperNounNeut',
            'NNeut')


def write_masculine_nouns(lemmas, lex_dir):
    # We separate animate from inanimate by adding all lemmas with explicitly
    # marked animate declensions to a set, then subtracting that set from the
    # set of all lemmas to get the inanimate ones.
    animate = set()
    all_lemmas = set()
    for l, msd in lemmas:
        if msd.endswith('say'):
            animate.add(l)
        all_lemmas.add(l)
    out = open(lex_dir + 'common_masc_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, animate, 'NounMascAnimate', 'NMascAn')
    write_lexicon_to_open_file(out, all_lemmas - animate,
            'NounMascInanimate', 'NMascIn')
    out.close()


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
    out.close()


def write_neuter_nouns(lemmas, lex_dir):
    e_lemmas = set()
    o_lemmas = set()
    for l in lemmas:
        if l.endswith('e'):
            e_lemmas.add(l)
        else:
            o_lemmas.add(l)
    out = open(lex_dir + 'common_neut_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, o_lemmas, 'NounNeutO', 'NNeutO')
    write_lexicon_to_open_file(out, e_lemmas, 'NounNeutE', 'NNeutE')
    out.close()


def write_adjectives(lemmas, lex_dir):
    i_lemmas = set()
    poss_lemmas = set()
    part_lemmas = set()
    other_lemmas = set()
    for l in lemmas:
        if l.endswith('i'):
            i_lemmas.add(l)
        elif l.endswith('ev') or l.endswith('ov'):
            poss_lemmas.add(l)
        elif (l.endswith(u'oč'.encode('utf-8')) or
                l.endswith(u'eč'.encode('utf-8'))):
            part_lemmas.add(l)
        else:
            other_lemmas.add(l)
    out = open(lex_dir + 'adjs.lexc', 'w')
    write_lexicon_to_open_file(out, i_lemmas, 'AdjI', 'AdjInfI')
    write_lexicon_to_open_file(out, poss_lemmas, 'AdjPoss', 'AdjInfPoss')
    write_lexicon_to_open_file(out, part_lemmas, 'AdjPart', 'AdjInfPart')
    write_lexicon_to_open_file(out, other_lemmas, 'AdjNormal', 'AdjInf')
    out.close()


def write_verbs(lemmas, lex_dir):
    progressive = set()
    perfective = set()
    biaspectual = set()
    biti = set(['biti'])
    for l, msd in lemmas:
        if msd[2] == 'b':
            biaspectual.add(l)
        elif msd[2] == 'e':
            perfective.add(l)
        elif msd[2] == 'p':
            progressive.add(l)
        else:
            # The only other option is '-', which only happens with biti
            pass
    out = open(lex_dir + 'verbs.lexc', 'w')
    write_lexicon_to_open_file(out, progressive, 'VerbProg', 'VProgInf')
    write_lexicon_to_open_file(out, perfective, 'VerbPerf', 'VPerfInf')
    write_lexicon_to_open_file(out, biaspectual, 'VerbBi', 'VBiInf')
    write_lexicon_to_open_file(out, biti, 'VerbBiti', 'BitiInf')
    out.close()


def write_prepositions(lemmas, lex_dir):
    nom = set()
    gen = set()
    dat = set()
    acc = set()
    loc = set()
    ins = set()
    for l, msd in lemmas:
        if msd[1] == 'n':
            nom.add(l)
        elif msd[1] == 'g':
            gen.add(l)
        elif msd[1] == 'd':
            dat.add(l)
        elif msd[1] == 'a':
            acc.add(l)
        elif msd[1] == 'l':
            loc.add(l)
        elif msd[1] == 'i':
            ins.add(l)
    out = open(lex_dir + 'prepositions.lexc', 'w')
    write_lexicon_to_open_file(out, nom, 'Prep', 'PrepNom')
    write_lexicon_to_open_file(out, gen, 'Prep', 'PrepGen')
    write_lexicon_to_open_file(out, dat, 'Prep', 'PrepDat')
    write_lexicon_to_open_file(out, acc, 'Prep', 'PrepAcc')
    write_lexicon_to_open_file(out, loc, 'Prep', 'PrepLoc')
    write_lexicon_to_open_file(out, ins, 'Prep', 'PrepIns')
    out.close()


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
