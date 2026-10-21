"""Local paths and simple heading anchors; this is not a Markdown renderer."""

import re
from urllib.parse import unquote


def assert_markdown_links(test, documents, boundary):
    linked = set()
    for document in documents:
        test.assertTrue(document.is_file(), f"Missing document: {document}")
        links = re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", document.read_text())
        for link in links:
            if link.startswith(("https:", "http:")):
                continue
            with test.subTest(document=str(document), link=link):
                path, _, fragment = unquote(link).partition("#")
                target = (document.parent / path).resolve() if path else document
                test.assertTrue(target.is_relative_to(boundary))
                test.assertTrue(target.is_file(), f"Missing resource: {link}")
                linked.add(target)
                if fragment:
                    headings = re.findall(r"^#{1,6} (.+)$", target.read_text(), re.MULTILINE)
                    anchors = {
                        re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                        for heading in headings
                    }
                    test.assertIn(fragment, anchors, f"Missing heading: {link}")
    return linked
