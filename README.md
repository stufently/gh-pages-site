# gh-pages-site

A reusable GitHub Actions workflow that turns a repository's `README.md` (and `docs/*.md`)
into a small landing + docs site on GitHub Pages at `https://<owner>.github.io/<repo>/`.
Built for search engines and AI search: every site gets `llms.txt`, `llms-full.txt`,
`sitemap.xml`, `robots.txt`, schema.org JSON-LD (`SoftwareApplication`, `FAQPage`,
`TechArticle`), canonical URLs and Open Graph tags.

The generator is plain Python standard library — no pip install, no Node, no theme.

## What the site contains

- `/` — landing: headline, description, feature cards, chosen README sections
  (for example *Install* and *Examples*), FAQ, list of doc pages.
- `/docs/` — the full README with a table of contents.
- `/docs/<slug>/` — one page per extra markdown file (`pages` in the config) and per
  top-level `docs/*.md`.
- `404.html`, `sitemap.xml` (with `lastmod` from git), `robots.txt`, `llms.txt`,
  `llms-full.txt`.

Relative links in the markdown are rewritten: to a site page when the target is rendered,
otherwise to the file on GitHub. Since v1.0.1 the same applies to `src`/`href` in raw HTML
blocks (`<img src="docs/x.png" width="…">`): images go to `raw.githubusercontent.com`,
absolute URLs, `data:`/`mailto:` and other schemes stay as written. The build fails on a
broken internal link or anchor, invalid JSON-LD, a wrong canonical URL or unbalanced HTML.

## Install into a repo

1. Clone this repo next to the tool repo and run the installer:

   ```bash
   git clone https://github.com/stufently/gh-pages-site ~/github/gh-pages-site
   bash ~/github/gh-pages-site/install.sh ~/github/<repo>
   ```

   It writes `.github/workflows/pages.yml` pinned to the latest tag of this repo by commit
   SHA and creates `.github/site/site.toml` from the example. It stops if the repo already
   has another Pages workflow.

2. Fill in `.github/site/site.toml` from facts in the README: `name`, `title`, `headline`,
   `description`, `lang` (`en` or `ru`), `keywords`, `landing_sections` (exact `##` titles
   from the README), `pages` (extra markdown files), `features`, `[[faq]]`. See
   [templates/site.toml](templates/site.toml) for every key.

3. Optional: `.github/site/extra.css` is appended to the stylesheet.

4. Build locally to check (Docker, nothing installed on the host):

   ```bash
   docker run --rm -v "$PWD":/app -v ~/github/gh-pages-site:/gen:ro -w /app \
     -e GITHUB_REPOSITORY=<owner>/<repo> python:3.15-slim python3 /gen/site/build.py _site
   ```

5. Enable Pages with GitHub Actions as the source, then merge:

   ```bash
   gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow
   ```

The caller workflow builds on every pull request that touches any markdown file or the site
config, and deploys from the default branch. It never creates tags or releases.

## Calling the workflow by hand

```yaml
jobs:
  site:
    uses: stufently/gh-pages-site/.github/workflows/pages.yml@<commit-sha> # v1.1.0
    permissions:
      contents: read
      pages: write
      id-token: write
```

Inputs: `python_version` (default `3.15`), `deploy` (default `true`; pull requests never
deploy). The generator is checked out at the called workflow's own commit
(`job.workflow_sha`), so the `uses:` pin is the only version to bump. `generator_ref` is
deprecated and ignored (a warning is printed if it differs); it stays declared so older
callers keep working.

## Releases

- v1.1.0 — the generator is checked out at the called workflow's own commit; `generator_ref`
  is deprecated and ignored, so a dependabot bump of `uses:` updates the generator too.
- v1.0.1 — relative `src`/`href` in raw HTML blocks resolve like markdown links.
- v1.0.0 — first release.

## License

MIT
