"""Writes repo/README.md, LICENSE, jurisdiction.json from corpus.json."""
import json
import os

from state_lib import write_docs

HERE = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(os.path.join(HERE, 'corpus.json'), encoding='utf-8'))
const = [a for a in c['acts'] if a['slug'].startswith('constitution-')]
code = [a for a in c['acts'] if a['slug'].startswith('chapter-')]
n = lambda acts: sum(len(a['versions'][0]['units']) for a in acts)
rows = [('constitution-*/', 'Constitution of North Dakota, one folder per article, plus the preamble, transition schedule and Enabling Act', 1, f'{len(const)} folders, {n(const)} provisions, dated 2026-10-29'),
        ('chapter-*/', 'North Dakota Century Code, Titles 12.1 (Criminal Code), 47 (Property) and 10 (Corporations), one folder per chapter', 1,
         f'{len(code)} chapters, {n(code)} sections, dated 2026-02-03')]
write_docs(HERE, {
    'name': 'United States (North Dakota)', 'state': 'North Dakota', 'code': 'US-ND', 'slug': 'north-dakota',
    'domain': 'ndlegis.gov', 'acts_table': rows,
    'source': 'The [North Dakota Century Code](https://ndlegis.gov/general-information/north-dakota-century-code) and the [Constitution of North Dakota](https://ndlegis.gov/constitution), published by the North Dakota Legislative Council, one PDF per chapter or article. English. The site states that the text it publishes "is the official version of the North Dakota Century Code".',
    'dates': 'The Legislative Council publishes only the current text. Each act is therefore one version, "oldest version available". The Century Code chapters are dated 2026-02-03, the date of the site\'s note that "all statutory changes approved during the 2026 special session are now reflected on this website"; the Constitution states no currency date and is dated 2026-10-29, the day before it was retrieved (2026-10-30), so that no commit lies in the future of the build. Later builds will add later versions on top.',
    'limits': 'A first build: the Constitution and Titles 10, 12.1 and 47 of the Century Code. The other titles, the session laws and the Administrative Code are not included. There is no history before the dates above.',
    'license': """Source: North Dakota Legislative Council, https://ndlegis.gov/ (retrieved 2026-10-30).

Statute text is not copyrightable: under the government edicts doctrine, as the Supreme Court applied it in Georgia v.
Public.Resource.Org, Inc., 590 U.S. 255 (2020), no one holds copyright in the laws that legislators make in their
official capacity. The site states no restriction on reuse of the Century Code or the Constitution.""",
})
