"""Raw HTML blocks in README: relative src/href resolve like markdown links."""
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

BUILD = pathlib.Path(__file__).resolve().parent.parent / "site" / "build.py"

README = """# Demo

Intro paragraph.

## Install

<img src="docs/x.png" alt="shot" width="360">

<p><a href="docs/guide.md#usage">Guide</a> <a href='LICENSE'>License</a></p>

<a href="https://example.com/a.png">abs</a> <img src="data:image/png;base64,AA"> <a href="#install">top</a> <a href="mailto:a@b.c">m</a> <a href="tel:+100">t</a>

<img
  src="docs/x.png" alt="multi">

<div><img src=docs/x.png alt="bare"> <a href=" https://example.com/sp ">sp</a></div>

<pre><code>&lt;a href="LICENSE"&gt;</code></pre>

## Docs

<img src="docs/x.png" width="820">
"""

GUIDE = "# Guide\n\n## Usage\n\nText.\n"

CONFIG = """repository = "acme/demo"
name = "Demo"
title = "Demo"
headline = "Demo"
description = "Demo site."
landing_sections = ["Install"]
features = ["One."]
[[faq]]
q = "Q?"
a = "A."
"""

RAW = "https://raw.githubusercontent.com/acme/demo/main/docs/x.png"


class RawHtmlLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(cls.tmp.name)
        (root / "docs").mkdir()
        (root / ".github/site").mkdir(parents=True)
        (root / "README.md").write_text(README, encoding="utf-8")
        (root / "docs/guide.md").write_text(GUIDE, encoding="utf-8")
        (root / "docs/x.png").write_bytes(b"\x89PNG")
        (root / "LICENSE").write_text("MIT", encoding="utf-8")
        (root / ".github/site/site.toml").write_text(CONFIG, encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_REPOSITORY", "SITE_CONFIG")}
        r = subprocess.run([sys.executable, str(BUILD), "_site"], cwd=root, env=env,
                           capture_output=True, text=True)
        cls.rc, cls.log = r.returncode, r.stdout + r.stderr
        cls.home = (root / "_site/index.html").read_text(encoding="utf-8") if r.returncode == 0 else ""
        cls.docs = (root / "_site/docs/index.html").read_text(encoding="utf-8") if r.returncode == 0 else ""

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_build_passes_self_check(self):
        self.assertEqual(self.rc, 0, self.log)

    def test_img_goes_to_raw_and_keeps_width(self):
        self.assertIn(f'<img src="{RAW}" alt="shot" width="360">', self.docs)
        self.assertIn(f'<img src="{RAW}" width="820">', self.docs)
        self.assertIn(f'<img src="{RAW}" alt="shot" width="360">', self.home)

    def test_multiline_and_unquoted_attributes(self):
        self.assertIn(f'<img\n  src="{RAW}" alt="multi">', self.docs)
        self.assertIn(f'<img src="{RAW}" alt="bare">', self.docs)

    def test_escaped_code_and_spaced_absolute_untouched(self):
        self.assertIn('<pre><code>&lt;a href="LICENSE"&gt;</code></pre>', self.docs)
        self.assertIn('<a href=" https://example.com/sp ">sp</a>', self.docs)

    def test_md_link_goes_to_site_page(self):
        self.assertIn('<a href="../docs/guide/#usage">Guide</a>', self.docs)
        self.assertIn('<a href="docs/guide/#usage">Guide</a>', self.home)

    def test_other_file_goes_to_blob(self):
        self.assertIn("<a href='https://github.com/acme/demo/blob/main/LICENSE'>License</a>", self.docs)

    def test_absolute_data_mailto_and_anchor_untouched(self):
        self.assertIn('<a href="https://example.com/a.png">abs</a>', self.docs)
        self.assertIn('<img src="data:image/png;base64,AA">', self.docs)
        self.assertIn('<a href="mailto:a@b.c">m</a>', self.docs)
        self.assertIn('<a href="tel:+100">t</a>', self.docs)
        self.assertIn('<a href="#install">top</a>', self.docs)


if __name__ == "__main__":
    unittest.main()
