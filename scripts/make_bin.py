#!/usr/bin/env python

from subprocess import Popen, PIPE


def main(lexica, foma_file, override_files):
    proc = Popen('cat %s > lexicon.lexc' % ' '.join(lexica), shell=True)
    proc.wait()
    proc = Popen('cat %s > overrides.lexc' % ' '.join(override_files),
            shell=True)
    proc.wait()
    proc = Popen(('foma', '-l', foma_file))
    proc.wait()
    proc = Popen('rm -f lexicon.lexc', shell=True)
    proc.wait()
    proc = Popen('rm -f overrides.lexc', shell=True)
    proc.wait()


if __name__ == '__main__':
    from test import get_test_description_from_args
    to_test, _ = get_test_description_from_args()
    if len(to_test) != 1:
        print 'Must specify exactly one binary to create'
        exit(-1)
    desc = to_test[0]
    foma_file = 'foma/slovene.foma'
    main(desc['lexica'], foma_file, desc['overrides'])


# vim: et sw=4 sts=4
