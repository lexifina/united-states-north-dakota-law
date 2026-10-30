"""Parse the cached ndlegis.gov PDFs into corpus.json. Reads only .cache; no network."""
import json
import os
import re
import sys

import pymupdf

from state_lib import Act, Fetcher, key, norm, sha, text_of, write_corpus

HERE = os.path.dirname(os.path.abspath(__file__))
F = Fetcher(HERE, 'x')
RETRIEVED = '2026-10-30'
CODE_DATE = '2026-02-03'    # "02/03/26 UPDATE: All statutory changes approved during the 2026 special session are now reflected on this website."
CONST_DATE = '2026-10-29'   # day before retrieval: commits are dated noon local time, so the retrieval day would lie in the future
MARK = re.compile(r'^(\d{1,2}\.|[a-z]{1,2}\.|\([0-9a-z]{1,4}\))$')
SEC = re.compile(r'^(\d+(?:\.\d+)?-\d+(?:\.\d+)?-\d+(?:\.\d+)?)\.\s+(.*)$')


def paragraphs(raw_lines):
    """A line that ends in a space is wrapped onto the next one; a line that does not ends its paragraph. A numbering
    marker alone on a line (1., a., (1)) is put in front of the paragraph that follows."""
    out, cur, prefix = [], '', ''
    for raw in raw_lines:
        s = raw.rstrip('\n')
        t = norm(s)
        if not t or re.fullmatch(r'Page No\. \d+', t):
            continue
        if cur and SEC.match(t):        # a section heading always starts a paragraph, even after a line that ended in a space
            out.append((prefix + ' ' + cur).strip())
            cur, prefix = '', ''
        if MARK.match(t) and not cur:
            prefix = (prefix + ' ' + t).strip()
            continue
        cur = (cur + ' ' + t).strip()
        if not s.endswith(' '):
            out.append((prefix + ' ' + cur).strip())
            cur, prefix = '', ''
    if cur:
        out.append((prefix + ' ' + cur).strip())
    return out


def pdf_paragraphs(b):
    d = pymupdf.open(stream=b, filetype='pdf')
    lines = []
    for p in d:
        lines += p.get_text().split('\n')
    return paragraphs(lines)


def statutes(man):
    acts = []
    for tnum in ('12.1', '47', '10'):
        t = man['titles'][tnum]
        for ch in t['chapters']:
            m = re.match(r'Chapter ([0-9.]+-[0-9.]+) - (.*)$', ch['name'])
            cid, cname = (m.group(1), m.group(2)) if m else (ch['name'], '')
            known = {a for a, _ in ch['sections']}
            a = Act('chapter-' + re.sub(r'[^0-9a-z]+', '-', cid.lower()), f'N.D.C.C. ch. {cid}',
                    f'North Dakota Century Code, Chapter {cid}: {cname}', f'https://ndlegis.gov/cencode/{ch["pdfs"][0]}' if ch['pdfs'] else man['index'],
                    CODE_DATE)
            raws = b''
            cur = None
            for pdf in ch['pdfs']:
                b = F.cached(f'https://ndlegis.gov/cencode/{pdf}')
                if b is None:
                    continue
                raws += b
                for para in pdf_paragraphs(b):
                    m = SEC.match(para)
                    if m and m.group(1) in known:
                        if cur:
                            a.add(*cur_unit(cur))
                        cur = {'num': m.group(1), 'lines': ['# ' + para]}
                    elif cur:
                        cur['lines'].append(para)
            if cur:
                a.add(*cur_unit(cur))
            a.sha256 = sha(raws)
            acts.append(a)
    return acts


def cur_unit(cur):
    return (key('sec', cur['num'], 3), 'N.D.C.C. ' + cur['num'], 'section', text_of(cur['lines']))


def constitution(man):
    acts = []
    for i, c in enumerate(man['constitution']):
        b = F.cached(c['url'])
        paras = pdf_paragraphs(b)
        name = c['name']
        slug = re.sub(r'[^a-z0-9]+', '-', os.path.basename(c['url'])[:-4].lower())
        a = Act('constitution-' + slug, 'N.D. Const. ' + name.split(' ')[0] + (' ' + name.split(' ')[1] if name.startswith('Article') else ''),
                'Constitution of North Dakota: ' + name, c['url'], CONST_DATE, sha256=sha(b))
        cur, head = None, []
        for para in paras:
            m = re.match(r'^Section (\d+)\.\s', para)
            if m:
                if cur:
                    a.add(*const_unit(cur))
                cur = {'num': m.group(1), 'lines': [para]}
            elif cur:
                cur['lines'].append(para)
            else:
                head.append(para)       # the article's title lines, or the whole text of the preamble or a schedule
        if cur:
            a.add(*const_unit(cur))
            if cur and len(head) > 2:
                a.add('intro', 'Introductory text', 'preamble', text_of(head))
        elif head:
            body = [h for h in head if h.upper() != h or len(h) > 60]
            a.add('text', name, 'text', text_of(['# ' + head[0]] + head[1:]))
        acts.append(a)
    return acts


def const_unit(cur):
    first = cur['lines'][0]
    cur['lines'][0] = '# ' + first
    return (key('sec', cur['num'], 3), f'Section {cur["num"]}', 'section', text_of(cur['lines']))


def main():
    man = json.load(open(os.path.join(HERE, '.cache', 'manifest.json')))
    acts = constitution(man) + statutes(man)
    country = {'code': 'US-ND', 'name': 'United States (North Dakota)', 'slug': 'united-states-north-dakota', 'lang': 'en',
               'tz': 'America/Chicago', 'future_branch': 'future',
               'publisher': {'name': 'North Dakota Legislative Council', 'email': 'cencode@ndlegis.gov.invalid'},
               'default_in_force_rule': {'text': 'No dated history is published: each act is the oldest version available, dated by the source\'s own currency statement.',
                                         'source': 'https://ndlegis.gov/general-information/north-dakota-century-code'},
               'licence_note': 'Statute text is not copyrightable (Georgia v. Public.Resource.Org, 2020). Source: North Dakota Legislative Council, the official Century Code.'}
    sources = [{'name': 'North Dakota Century Code (Legislative Council)', 'url': 'https://ndlegis.gov/general-information/north-dakota-century-code',
                'retrieved': RETRIEVED,
                'licence': 'Statute text carries no copyright (Georgia v. Public.Resource.Org, 2020). The site states that the text published on it is the official version of the Century Code and states no restriction on reuse; robots.txt allows /cencode/ and /constit/.',
                'notes': 'Titles 10, 12.1 and 47, one PDF per chapter. The page states "02/03/26 UPDATE: All statutory changes approved during the 2026 special session are now reflected on this website."'},
               {'name': 'Constitution of North Dakota (Legislative Council)', 'url': 'https://ndlegis.gov/constitution', 'retrieved': RETRIEVED,
                'licence': 'As above.', 'notes': 'One PDF per article, the preamble, the transition schedule and the Enabling Act.'}]
    decisions = [
        'Each act is a single "oldest version available": the Legislative Council publishes only the current text of each chapter, with no dated history.',
        f'Century Code acts are dated {CODE_DATE}, the date of the site\'s own note that all changes approved in the 2026 special session are reflected. The Constitution pages state no currency date, so its acts are dated {CONST_DATE}, the day before retrieval ({RETRIEVED}): commits are dated noon local time, and a commit dated the retrieval day would lie in the future of the build.',
        'One act per chapter of the Century Code and one per Constitution article; one unit per section, keyed by the section number the Code prints. Section numbers are checked against the chapter\'s section list on the Century Code index page.',
        'Paragraphs are rebuilt from the PDF text layer: a line that ends in a space is wrapped onto the next one, and a numbering marker alone on a line, such as 1. or a., is put in front of the paragraph that follows. Page numbers ("Page No. 5") are dropped.']
    write_corpus(HERE, country, sources, acts, decisions)


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    main()
