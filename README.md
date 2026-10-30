# United States (North Dakota): law history in git

The law of North Dakota as a git history: one file per provision, with `git blame` and `git log` working line by line. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now (a first build, not complete)**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution-*/` | Constitution of North Dakota, one folder per article, plus the preamble, transition schedule and Enabling Act | 1 | 19 folders, 195 provisions, dated 2026-10-29 |
| `chapter-*/` | North Dakota Century Code, Titles 12.1 (Criminal Code), 47 (Property) and 10 (Corporations), one folder per chapter | 1 | 110 chapters, 1927 sections, dated 2026-02-03 |

**Source.** The [North Dakota Century Code](https://ndlegis.gov/general-information/north-dakota-century-code) and the [Constitution of North Dakota](https://ndlegis.gov/constitution), published by the North Dakota Legislative Council, one PDF per chapter or article. English. The site states that the text it publishes "is the official version of the North Dakota Century Code".

## Dates

The Legislative Council publishes only the current text. Each act is therefore one version, "oldest version available". The Century Code chapters are dated 2026-02-03, the date of the site's note that "all statutory changes approved during the 2026 special session are now reflected on this website"; the Constitution states no currency date and is dated 2026-10-29, the day before it was retrieved (2026-10-30), so that no commit lies in the future of the build. Later builds will add later versions on top.

## How it is checked

Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`) and must match `corpus.json`; the results are in `REPRODUCE.md`.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist (`<law key>@ndlegis.gov.invalid`). In this first build no dated history is available, so every commit is credited to the publisher as "oldest version available". The committer is always Lexifina.

## Limits

A first build: the Constitution and Titles 10, 12.1 and 47 of the Century Code. The other titles, the session laws and the Administrative Code are not included. There is no history before the dates above.
