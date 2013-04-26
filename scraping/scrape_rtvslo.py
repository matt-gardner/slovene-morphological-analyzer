#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from collections import defaultdict
from subprocess import Popen, PIPE

def main():
    counts = get_word_counts()
    print 'Loading known forms'
    test_file = open('../tests/everything.tsv')
    forms = set()
    seen_counts = defaultdict(int)
    unseen_words = set()
    for line in test_file:
        forms.add(line.split('\t')[0])
    for word in counts:
        encoded_word = word.encode('utf-8')
        if encoded_word in forms or lower_case(word) in forms:
            seen_counts['seen'] += counts[word]
        else:
            seen_counts['unseen'] += counts[word]
            unseen_words.add(word)
    print 'Unseen words:'
    proc = Popen(('flookup', '../slovene.bin'), stdin=PIPE, stdout=PIPE)
    for word in unseen_words:
        proc.stdin.write('%s\n' % word.encode('utf-8'))
    proc.stdin.close()
    parses = defaultdict(set)
    for line in proc.stdout:
        if line.isspace(): continue
        try:
            form, analysis = line.strip().split('\t')
        except ValueError:
            print 'Bad line from stdout:', line
            exit(-1)
        parses[form].add(analysis)
    proc.stdout.close()
    unparseable = 0
    print 'Unparseable:'
    for word in unseen_words:
        if '+?' in parses[word]:
            unparseable += 1
            print word, counts[word]
        #else:
            #print word, counts[word], ',', len(parses[word]), 'parses'
    unseen = seen_counts['unseen']
    seen = seen_counts['seen']
    percent = float(unseen) / (unseen + seen)
    percent_unparseable = float(unparseable) / (unseen + seen)
    print 'Seen: %d; Unseen: %d; Percent unseen: %.3f' % (seen, unseen,
            percent)
    print 'Unparseable: %d; Percent unparseable: %.3f' % (unparseable,
            percent_unparseable)


def lower_case(word):
    word = word.lower()
    word = word.replace(u'Č', u'č')
    word = word.replace(u'Š', u'š')
    word = word.replace(u'Ž', u'ž')
    return word.encode('utf-8')


def get_word_counts():
    site_base = 'http://www.rtvslo.si'
    html = urlopen_with_chrome(site_base)
    soup = BeautifulSoup(html)
    story_links = []
    for lead in soup.findAll(attrs={'class':'lead_menu_item_details'}):
        link = dict(lead.find(attrs={'class':'title'}).attrs)['href']
        story_links.append(site_base + link)
    texts = []
    for link in story_links:
        print 'Scraping story', link
        html = urlopen_with_chrome(link)
        soup = BeautifulSoup(html)
        paragraphs = soup.findAll('p')
        text = ''
        for p in paragraphs:
            text += ' '.join(p.findAll(text=True)) + '\n'
        texts.append(text)
    counts = defaultdict(int)
    for text in texts:
        to_remove = ['"', ',', '.', ':', '(', ')', '?', ';', u'”', u'“', '!',
                "'"]
        for char in to_remove:
            text = text.replace(char, '')
        text = text.split()
        for word in text:
            if '--' in word or '@' in word or '/' in word:
                continue
            if word == '-':
                continue
            counts[word] += 1
    words = counts.keys()
    words.sort(key=lambda x: counts[x])
    #for word in words:
        #print '%10s: %5d' % (word, counts[word])
    return counts


def urlopen_with_chrome(url):
    import urllib2
    opener = urllib2.build_opener()
    request = urllib2.Request(url)
    request.add_header('User-Agent',
            'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.13 '
            '(KHTML, like Gecko) Chrome/9.0.597.84 Safari/534.13')
    html = opener.open(request).read()
    return html


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
