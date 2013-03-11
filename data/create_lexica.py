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
    conjunctions = set()
    particles = set()
    interjections = set()
    abbreviations = set()
    residuals = set()
    adverbs = set()
    pronouns = set()
    numerals = set()
    for line in gzip.open(sloleks_file):
        form, lemma, msd, freq, irreg = line.split('\t')
        if '*' in irreg: continue
        if msd.startswith('Npm'):
            npms.add((lemma, msd))
        elif msd.startswith('Npf'):
            npfs.add((lemma, msd, form))
        elif msd.startswith('Npn'):
            npns.add(lemma)
        elif msd.startswith('Ncm'):
            ncms.add((lemma, msd))
        elif msd.startswith('Ncf'):
            ncfs.add(lemma)
        elif msd.startswith('Ncn'):
            ncns.add(lemma)
        elif msd[0] == 'A':
            adjs.add((lemma, msd, form))
        elif msd[0] == 'V':
            verbs.add((lemma, msd))
        elif msd[0] == 'S':
            prepositions.add((lemma, msd))
        elif msd[0] == 'C':
            conjunctions.add((lemma, msd))
        elif msd[0] == 'Q':
            particles.add(lemma)
        elif msd[0] == 'I':
            interjections.add(lemma)
        elif msd[0] == 'Y':
            abbreviations.add(lemma)
        elif msd[0] == 'X':
            residuals.add(lemma)
        elif msd[0] == 'R':
            adverbs.add((lemma, msd))
        elif msd[0] == 'P':
            pronouns.add((lemma, msd))
        elif msd[0] == 'M':
            numerals.add((lemma , msd))
        else:
            raise RuntimeError("Found an MSD category I didn't recognize: " +
                    msd[0])
    write_masculine_nouns(ncms, lex_dir)
    write_feminine_nouns(ncfs, lex_dir)
    write_neuter_nouns(ncns, lex_dir)
    write_p_masculine_nouns(npms, lex_dir)
    write_p_feminine_nouns(npfs, lex_dir)
    write_p_neuter_nouns(npns, lex_dir)
    write_masculine_nouns(ncms, lex_dir)
    write_feminine_nouns(ncfs, lex_dir)
    write_neuter_nouns(ncns, lex_dir)
    write_adjectives(adjs, lex_dir)
    write_verbs(verbs, lex_dir)
    write_prepositions(prepositions, lex_dir)
    write_conjunctions(conjunctions, lex_dir)
    write_adverbs(adverbs, lex_dir)
    write_pronouns(pronouns, lex_dir)
    write_numerals(numerals, lex_dir)
    write_lexicon(lex_dir+'particles.lexc', particles, 'Particle', 'PartInf')
    write_lexicon(lex_dir+'interjections.lexc', interjections, 'Interjection',
            'InterjInf')
    write_lexicon(lex_dir+'abbreviations.lexc', abbreviations, 'Abbrev',
            'AbbrevInf')
    write_lexicon(lex_dir+'residuals.lexc', residuals, 'Residual', 'ResidInf')


def no_fleeting_e(lemma, msd, form):
    # Currently intended for use with adjectives; possibly could be extended
    # later to also deal with nouns, but this initial test is probably wrong
    # for nouns.
    if not lemma.endswith('en'):
        return False
    # Because every possible MSD gets fed into this method, we only need to
    # catch the non-fleeting e in one of the forms.  So we go with the
    # masculine plural accusative.
    if 'mpa' in msd:
        if form.endswith('ene'):
            return True
    return False


def detect_indeclinable(lemma, msd, form):
    # Again here we only need to use a single form for this; we'll use feminine
    # plural dative.
    if 'fpd' in msd:
        if form == lemma:
            return True
    return False


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
    write_lexicon_to_open_file(out, animate, 'Noun', 'NMascAn')
    write_lexicon_to_open_file(out, all_lemmas - animate, 'Noun', 'NMascIn')
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
    consonant = ost_lemmas.union(other_lemmas)
    out = open(lex_dir + 'common_fem_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, a_lemmas, 'Noun', 'NFemA')
    write_lexicon_to_open_file(out, ev_lemmas, 'Noun', 'NFemEv')
    write_lexicon_to_open_file(out, consonant, 'Noun', 'NFemOst')
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
    write_lexicon_to_open_file(out, o_lemmas, 'Noun', 'NNeutO')
    write_lexicon_to_open_file(out, e_lemmas, 'Noun', 'NNeutE')
    out.close()


# Proper nouns are just a quick copy and paste job for now, but will need some
# serious attention.

def write_p_masculine_nouns(lemmas, lex_dir):
    # We separate animate from inanimate by adding all lemmas with explicitly
    # marked animate declensions to a set, then subtracting that set from the
    # set of all lemmas to get the inanimate ones.
    animate = set()
    all_lemmas = set()
    for l, msd in lemmas:
        if msd.endswith('say'):
            animate.add(l)
        all_lemmas.add(l)
    out = open(lex_dir + 'proper_masc_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, animate, 'Noun', 'PNMascAn')
    write_lexicon_to_open_file(out, all_lemmas - animate, 'Noun', 'PNMascIn')
    out.close()


def write_p_feminine_nouns(lemmas, lex_dir):
    # Feminine surnames do not decline, so we separate them out.
    indeclinable = set()
    a_lemmas = set()
    ost_lemmas = set()
    ev_lemmas = set()
    other_lemmas = set()
    for l, msd, form in lemmas:
        if detect_indeclinable(l, msd, form):
            indeclinable.add(l)
        elif l.endswith('a'):
            a_lemmas.add(l)
        elif l.endswith('ev'):
            ev_lemmas.add(l)
        elif l.endswith('ost'):
            ost_lemmas.add(l)
        else:
            other_lemmas.add(l)
    consonant = ost_lemmas.union(other_lemmas)
    out = open(lex_dir + 'proper_fem_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, indeclinable, 'Noun', 'PNFemIndeclinable')
    write_lexicon_to_open_file(out, a_lemmas - indeclinable, 'Noun', 'PNFemA')
    write_lexicon_to_open_file(out, ev_lemmas - indeclinable, 'Noun', 'PNFemEv')
    write_lexicon_to_open_file(out, consonant - indeclinable, 'Noun',
            'PNFemOst')
    out.close()


def write_p_neuter_nouns(lemmas, lex_dir):
    e_lemmas = set()
    o_lemmas = set()
    for l in lemmas:
        if l.endswith('e'):
            e_lemmas.add(l)
        else:
            o_lemmas.add(l)
    out = open(lex_dir + 'proper_neut_nouns.lexc', 'w')
    write_lexicon_to_open_file(out, o_lemmas, 'Noun', 'PNNeutO')
    write_lexicon_to_open_file(out, e_lemmas, 'Noun', 'PNNeutE')
    out.close()


def write_adjectives(lemmas, lex_dir):
    i_lemmas = set()
    poss_lemmas = set()
    part_lemmas = set()
    other_lemmas = set()
    no_fleeting_e_lemmas = set()
    for l, msd, form in lemmas:
        if msd[1] == 'p':
            part_lemmas.add(l)
        elif msd[1] == 's':
            poss_lemmas.add(l)
        elif l.endswith('i'):
            i_lemmas.add(l)
        else:
            if no_fleeting_e(l, msd, form):
                no_fleeting_e_lemmas.add(l)
            else:
                other_lemmas.add(l)
    other_lemmas = other_lemmas - no_fleeting_e_lemmas
    out = open(lex_dir + 'adjectives.lexc', 'w')
    write_lexicon_to_open_file(out, i_lemmas, 'Adj', 'AdjInfI')
    write_lexicon_to_open_file(out, poss_lemmas, 'Adj', 'AdjInfPoss')
    write_lexicon_to_open_file(out, part_lemmas, 'Adj', 'AdjInfPart')
    write_lexicon_to_open_file(out, no_fleeting_e_lemmas, 'Adj',
            'AdjNoFleetingInf')
    write_lexicon_to_open_file(out, other_lemmas, 'Adj', 'AdjInf')
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
    write_lexicon_to_open_file(out, progressive, 'Verb', 'VProgInf')
    write_lexicon_to_open_file(out, perfective, 'Verb', 'VPerfInf')
    write_lexicon_to_open_file(out, biaspectual, 'Verb', 'VBiInf')
    write_lexicon_to_open_file(out, biti, 'Verb', 'BitiInf')
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


def write_conjunctions(lemmas, lex_dir):
    coordinating = set()
    subordinating = set()
    for l, msd in lemmas:
        if msd[1] == 'c':
            coordinating.add(l)
        elif msd[1] == 's':
            subordinating.add(l)
    out = open(lex_dir + 'conjunctions.lexc', 'w')
    write_lexicon_to_open_file(out, coordinating, 'Conj', 'ConjCoord')
    write_lexicon_to_open_file(out, subordinating, 'Conj', 'ConjSubord')
    out.close()


def write_adverbs(lemmas, lex_dir):
    general = set()
    participle = set()
    for l, msd in lemmas:
        if msd[1] == 'g':
            general.add(l)
        elif msd[1] == 'r':
            participle.add(l)
    out = open(lex_dir + 'adverbs.lexc', 'w')
    write_lexicon_to_open_file(out, general, 'Adverb', 'AdverbInf')
    write_lexicon_to_open_file(out, participle, 'Adverb', 'AdverbPart')
    out.close()


def write_pronouns(lemmas, lex_dir):
    personal = set()
    possessive = set()
    demonstrative = set()
    relative = set()
    reflexive_bound = set()
    general = set()
    interrogative = set()
    indefinite = set()
    negative = set()
    for l, msd in lemmas:
        if msd[1] == 'p':
            personal.add(l)
        elif msd[1] == 's':
            possessive.add(l)
        elif msd[1] == 'd':
            demonstrative.add(l)
        elif msd[1] == 'r':
            relative.add(l)
        elif msd[1] == 'x' and msd[-1] == 'b':
            reflexive_bound.add(l)
        elif msd[1] == 'g':
            general.add(l)
        elif msd[1] == 'q':
            interrogative.add(l)
        elif msd[1] == 'i':
            indefinite.add(l)
        elif msd[1] == 'z':
            negative.add(l)
    out = open(lex_dir + 'pronouns.lexc', 'w')
    write_lexicon_to_open_file(out, personal, 'Pronoun', 'PronPersonal')
    # Possessives are too hard to do automatically; we'll just put these in
    # pronouns_rules.lexc
    #write_lexicon_to_open_file(out, possessive, 'Pronoun', 'PronPoss')
    write_lexicon_to_open_file(out, demonstrative, 'Pronoun', 'PronDemon')
    write_lexicon_to_open_file(out, relative, 'Pronoun', 'PronRel')
    # We just do bound reflexvies here, and handle the small number of other
    # reflexives in pronoun_rules.lexc
    write_lexicon_to_open_file(out, reflexive_bound, 'Pronoun', 'PronBoundRefl')
    write_lexicon_to_open_file(out, general, 'Pronoun', 'PronGen')
    write_lexicon_to_open_file(out, interrogative, 'Pronoun', 'PronInterr')
    write_lexicon_to_open_file(out, indefinite, 'Pronoun', 'PronIndef')
    write_lexicon_to_open_file(out, negative, 'Pronoun', 'PronNeg')
    out.close()


def write_numerals(lemmas, lex_dir):
    digits_cardinal = set()
    digits_ordinal = set()
    roman_cardinal = set()
    roman_ordinal = set()
    cardinal = set()
    ordinal = set()
    pronominal = set()
    special = set()
    for l, msd in lemmas:
        if msd[1] == 'd':
            if msd[2] == 'c':
                digits_cardinal.add(l)
            elif msd[2] == 'o':
                digits_ordinal.add(l)
        elif msd[1] == 'r':
            if msd[2] == 'c':
                roman_cardinal.add(l)
            elif msd[2] == 'o':
                roman_ordinal.add(l)
        elif msd[1] == 'l':
            if msd[2] == 'c':
                cardinal.add(l)
            elif msd[2] == 'o':
                ordinal.add(l)
            elif msd[2] == 'p':
                pronominal.add(l)
            elif msd[2] == 's':
                special.add(l)
    out = open(lex_dir + 'numerals.lexc', 'w')
    write_lexicon_to_open_file(out, digits_cardinal, 'Numeral', 'NumDigCard')
    write_lexicon_to_open_file(out, digits_ordinal, 'Numeral', 'NumDigOrd')
    write_lexicon_to_open_file(out, roman_cardinal, 'Numeral', 'NumRomCard')
    write_lexicon_to_open_file(out, roman_ordinal, 'Numeral', 'NumRomOrd')
    write_lexicon_to_open_file(out, cardinal, 'Numeral', 'NumCardInf')
    write_lexicon_to_open_file(out, ordinal, 'Numeral', 'NumOrdInf')
    write_lexicon_to_open_file(out, pronominal, 'Numeral', 'NumPronInf')
    write_lexicon_to_open_file(out, special, 'Numeral', 'NumSpecInf')
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
