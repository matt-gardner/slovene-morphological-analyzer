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
            npms.add((lemma, msd, form))
        elif msd.startswith('Npf'):
            npfs.add((lemma, msd, form))
        elif msd.startswith('Npn'):
            npns.add(lemma)
        elif msd.startswith('Ncm'):
            ncms.add((lemma, msd, form))
        elif msd.startswith('Ncf'):
            ncfs.add(lemma)
        elif msd.startswith('Ncn'):
            ncns.add(lemma)
        elif msd[0] == 'A':
            adjs.add((lemma, msd, form))
        elif msd[0] == 'V':
            verbs.add((lemma, msd, form))
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
    write_masculine_nouns(ncms, lex_dir, common=True)
    write_feminine_nouns(ncfs, lex_dir)
    write_neuter_nouns(ncns, lex_dir)
    write_masculine_nouns(npms, lex_dir, common=False)
    write_p_feminine_nouns(npfs, lex_dir)
    write_p_neuter_nouns(npns, lex_dir)
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


def no_fleeting_e(lemma, msd, form, test, ending):
    e_index = lemma.rfind('e')
    if e_index == -1:
        return False
    consonant = lemma[e_index+1:]
    if len(consonant) > 2 or len(consonant) < 1:
        return False
    if test in msd:
        if form == lemma[:e_index+1] + consonant + ending:
            return True
        elif (consonant[-1] == 'r' and
                form == lemma[:e_index+1] + consonant + 'j' + ending):
            return True
    return False


def no_added_j(lemma, msd, form, test, ending):
    if not lemma[-1] == 'r':
        return False
    if test in msd:
        if form == lemma + ending:
            return True
    return False


def no_ni_to_ne(lemma, msd, form):
    if msd.endswith('r3p'):
        if lemma.endswith('niti') and form.endswith('nijo'):
            return True
    return False


def no_e_to_i(lemma, msd, form):
    if lemma.endswith('neti'):
        return False
    if msd.endswith('r3p'):
        if lemma.endswith('eti') and form.endswith('ejo'):
            return True
    return False


def detect_stem_change(lemma, msd, form, mode):
    n_stem = None
    a_stem = None
    if mode == 'present':
        if msd.endswith('r1p'):
            if lemma.endswith(u'či'.encode('utf-8')):
                n_stem = lemma[:-1]
            else:
                n_stem = lemma[:-2]
            a_stem = form[:-2]
    if mode == 'imperative':
        if msd.endswith('m1p'):
            if lemma.endswith(u'či'.encode('utf-8')):
                n_stem = lemma[:-1]
            else:
                n_stem = lemma[:-2]
            a_stem = form[:-2]
            if a_stem[-1] == 'j' and not (n_stem.endswith('va') and
                    a_stem.endswith('uj')):
                a_stem = a_stem[:-1]
    elif mode == 'infinitive':
        # Here, by definition, the lemma equals the form.
        return None
    elif mode == 'participle':
        if msd.endswith('p-sm'):
            if lemma.endswith(u'či'.encode('utf-8')):
                n_stem = lemma[:-1]
            else:
                n_stem = lemma[:-2]
            a_stem = form[:-1]
    if n_stem == None or a_stem == None:
        return None
    if n_stem != a_stem and not expected_stem_change(n_stem, a_stem, mode):
        return a_stem
        # This was for testing to see if there were other regularities to
        # capture; there certainly are, but I gave up, as most of them are only
        # very small regularities.
        #i = 0
        #while (i < len(n_stem) and i < len(a_stem) and
                #n_stem[i] == a_stem[i]):
            #i += 1
        #old = ''
        #j = i
        #while j < len(n_stem):
            #old += n_stem[j]
            #j += 1
        #new = ''
        #j = i
        #while j < len(a_stem):
            #new += a_stem[j]
            #j += 1
    return None


def expected_stem_change(normal_stem, actual_stem, mode):
    known_changes = [('ni', 'ne'), ('e', 'i')]
    if mode == 'imperative':
        known_changes.extend([('eva', 'uj'), ('ova', 'uj')])
    else:
        known_changes.extend([('eva', 'uje'), ('ova', 'uje')])
    for orig, change in known_changes:
        if (normal_stem[:-len(orig)] == actual_stem[:-len(change)] and
                normal_stem[-len(orig):] == orig and
                actual_stem[-len(change):] == change):
            return True
    return False


def detect_indeclinable(lemma, msd, form):
    # Again here we only need to use a single form for this; we'll use feminine
    # plural dative.
    if 'fpd' in msd:
        if form == lemma:
            return True
    return False


def write_masculine_nouns(lemmas, lex_dir, common=True):
    # I first tried to make sets for all of the different continuation classes
    # I might need.  But with multiple orthogonal features, that got unwieldly,
    # so I came up with this way, using flags to denote features instead of
    # disjoint sets, which I think works a lot better.
    animate = set()
    no_fleeting = set()
    no_added_j_lemmas = set()
    all_lemmas = set()
    for l, msd, form in lemmas:
        if msd.endswith('say'):
            animate.add(l)
        if no_fleeting_e(l, msd, form, 'msg', 'a'):
            no_fleeting.add(l)
        if no_added_j(l, msd, form, 'msg', 'a'):
            no_added_j_lemmas.add(l)
        all_lemmas.add(l)
    flags = defaultdict(list)
    for lemma in all_lemmas:
        if lemma in animate:
            flags[lemma].append('@P.ANIMATE.Y@')
        if lemma not in no_fleeting:
            flags[lemma].append('@P.FLEETING.REPLACE@')
        if lemma in no_added_j_lemmas:
            flags[lemma].append('@P.ADD_J.N@')
    if common:
        outfile = 'common_masc_nouns.lexc'
        continuation = 'NMascCommon'
    else:
        outfile = 'proper_masc_nouns.lexc'
        continuation = 'NMascProper'
    out = open(lex_dir + outfile, 'w')
    out.write('LEXICON %s\n\n' % 'Noun')
    all_lemmas = list(all_lemmas)
    all_lemmas.sort()
    for l in all_lemmas:
        out.write('%s:%s %s;\n' % (l, l + ''.join(flags[l]), continuation))
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
            if no_fleeting_e(l, msd, form, 'msg', 'ega'):
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

modes = ['present', 'infinitive', 'imperative', 'participle']

def write_verbs(lemmas, lex_dir):
    progressive = set()
    perfective = set()
    biaspectual = set()
    flags = defaultdict(set)
    stems = defaultdict(dict)
    for l, msd, form in lemmas:
        for mode in modes:
            new_stem = detect_stem_change(l, msd, form, mode)
            if new_stem:
                stems[l][mode] = new_stem
        if msd[2] == 'b':
            biaspectual.add(l)
        elif msd[2] == 'e':
            perfective.add(l)
        elif msd[2] == 'p':
            progressive.add(l)
        else:
            # The only other option is '-', which only happens with biti
            pass
        if no_ni_to_ne(l, msd, form):
            flags[l].add('@P.NiToNe.N@')
        if no_e_to_i(l, msd, form):
            flags[l].add('@P.EToI.N@')
    out = open(lex_dir + 'verbs.lexc', 'w')
    out.write('LEXICON %s\n\n' % 'Verb')
    write_verb_lemmas(out, 'VProgRegular', progressive, flags, stems)
    write_verb_lemmas(out, 'VPerfRegular', perfective, flags, stems)
    write_verb_lemmas(out, 'VBiRegular', biaspectual, flags, stems)
    out.close()


def write_verb_lemmas(out, cont, lemmas, flags, stems):
    lemmas = list(lemmas)
    lemmas.sort()
    for l in lemmas:
        irregular = False
        for mode in modes:
            if mode in stems[l]:
                irregular = True
        if not irregular:
            if l in flags:
                with_flags = l + ''.join(list(flags[l]))
                out.write('%s:%s %s;\n' % (l, with_flags, cont))
            else:
                out.write('%s %s;\n' % (l, cont))
        else:
            l_flags = ''
            if l in flags:
                l_flags = ''.join(list(flags[l]))
            if l.endswith(u'či'.encode('utf-8')):
                regular_stem = l[:-1] + l_flags
            else:
                regular_stem = l[:-2] + l_flags
            if 'Prog' in cont:
                aspect = '+Progressive'
            elif 'Perf' in cont:
                aspect = '+Perfective'
            elif 'Bi' in cont:
                aspect = '+Biaspectual'
            lemma = l + '+V+Main' + aspect
            if 'present' in stems[l]:
                stem = stems[l]['present'] + l_flags + '+StemChanged'
            else:
                stem = regular_stem
            out.write('%s:%s VPresentForms;\n' % (lemma, stem))
            if 'imperative' in stems[l]:
                stem = stems[l]['imperative'] + l_flags + '+StemChanged'
            else:
                stem = regular_stem
            out.write('%s:%s VImperativeForms;\n' % (lemma, stem))
            if 'infinitive' in stems[l]:
                stem = stems[l]['infinitive'] + l_flags + '+StemChanged'
            else:
                stem = regular_stem
            out.write('%s:%s VInfinitiveForms;\n' % (lemma, stem))
            if 'participle' in stems[l]:
                stem = stems[l]['participle'] + l_flags + '+StemChanged'
            else:
                stem = regular_stem
            out.write('%s:%s VParticipleForms;\n' % (lemma, stem))


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
