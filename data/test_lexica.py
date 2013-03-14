#!/usr/bin/env python

from create_lexica import *

def main():
    lemma = 'dospeti'
    msd = 'Vmem1p'
    form = 'dospimo'
    mode = 'imperative'
    print detect_stem_change(lemma, msd, form, mode)


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
