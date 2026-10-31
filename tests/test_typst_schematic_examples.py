"""Compile standalone examples and receiving contexts, never update HOME."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path(os.environ.get('SCHEMATIC_PLUGIN_ROOT', ROOT / 'config/codex/plugins/ryo-workflows'))
EXAMPLES = PLUGIN / 'skills/creating-and-editing-typst-schematics/assets/examples'
NAMES = ['multiscale', 'iterative-selection', 'cascade-and-flows', 'information-decomposition']
LABELS = [
    ['Microscale','Mesoscale','Macroscale','階層と適用範囲','モデル範囲'],
    ['Candidates','Select','Update','Stop','候補 α','選択へ','反復'],
    ['Transport','Feedback','輸送','帰還','𝐸','𝑘'],
    ['A only','Shared','B only','模式的','𝐴','𝐵'],
]
TOOLS = all(shutil.which(x) for x in ['typst', 'pdfinfo', 'pdftotext'])
# Only use already available packages. Never ask Typst to populate the real
# HOME cache or fetch dependencies as an incidental test-suite side effect.
PACKAGE_ROOTS = [
    Path(os.environ.get('TYPST_PACKAGE_PATH', Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'typst/packages')),
    Path(os.environ.get('TYPST_PACKAGE_CACHE_PATH', Path(os.environ.get('XDG_CACHE_HOME', Path.home()/'.cache'))/'typst/packages')),
]
REQUIRED_PACKAGES = [('cetz','0.5.3'), ('oxifmt','1.0.0')]
PACKAGE_SOURCES = {
    (name, version): next((root/'preview'/name/version for root in PACKAGE_ROOTS
                          if (root/'preview'/name/version/'typst.toml').is_file()), None)
    for name, version in REQUIRED_PACKAGES
}



def run(*args, package_root):
    environment = os.environ.copy()
    environment.update(TYPST_PACKAGE_PATH=str(package_root), TYPST_PACKAGE_CACHE_PATH=str(package_root))
    # Cached imports resolve locally. An unexpected new dependency must fail
    # instead of reaching the network during an ordinary repository test.
    environment.update(HTTPS_PROXY='http://127.0.0.1:9', HTTP_PROXY='http://127.0.0.1:9',
                       https_proxy='http://127.0.0.1:9', http_proxy='http://127.0.0.1:9',
                       NO_PROXY='', no_proxy='')
    p = subprocess.run(args, capture_output=True, text=True, timeout=60, env=environment)
    if p.returncode:
        raise AssertionError(p.stdout + p.stderr)
    return p.stdout


def host_source(slide=False):
    size = 'width:320mm,height:180mm,margin:10mm' if slide else 'paper:"a4",margin:20mm'
    pt = 20 if slide else 10
    unit = 1.1 if slide else .8
    imports = '\n'.join(f'#import "{name}.typ" as f{i}' for i, name in enumerate(NAMES))
    # The local figure style may differ. The surrounding text and page setup
    # must survive both imports and calls, checked by context AND PDF geometry.
    return f'''#set page({size})
#set text(font:("Noto Sans", "Noto Sans CJK JP"),size:{pt}pt)
{imports}
#let sentinel() = context {{
  assert(text.size == {pt}pt)
  assert(text.font == ("noto sans", "noto sans cjk jp"))
  assert(page.width == {"320mm" if slide else "210mm"})
  assert(page.height == {"180mm" if slide else "297mm"})
  [#metadata((size:text.size/1pt, font:text.font)) <host-settings>]
  [HOST SENTINEL]
}}
#sentinel()
#grid(columns:(1fr,1fr),gutter:6mm,
  f0.schematic(unit:{unit}mm,label-size:{9.5 if slide else 7}pt),
  f1.schematic(unit:{unit}mm,label-size:{9.5 if slide else 7}pt),
  f2.schematic(unit:{unit}mm,label-size:{9.5 if slide else 7}pt),
  f3.schematic(unit:{unit}mm,label-size:{9.5 if slide else 7}pt))
#sentinel()
'''


@unittest.skipUnless(TOOLS and all(PACKAGE_SOURCES.values()), 'Typst, Poppler and cached CeTZ 0.5.3 / oxifmt 1.0.0 required')
class SchematicExampleTests(unittest.TestCase):
    def test_standalone_and_hosts_after_relocation(self):
        with tempfile.TemporaryDirectory(prefix='schematic-examples-', dir='/tmp') as tmp:
            package_root = Path(tmp)/'packages'
            for (name, version), source in PACKAGE_SOURCES.items():
                shutil.copytree(source, package_root/'preview'/name/version)
            def execute(*args):
                return run(*args, package_root=package_root)
            target = Path(os.environ.get('SCHEMATIC_EXAMPLE_EVIDENCE_DIR', tmp))
            target.mkdir(parents=True, exist_ok=True)
            for name in NAMES:
                shutil.copy2(EXAMPLES / f'{name}.typ', target)
            for name, labels in zip(NAMES, LABELS):
                with self.subTest(name=name):
                    pdf = target / f'{name}.pdf'
                    execute('typst', 'compile', str(target / f'{name}.typ'), str(pdf))
                    self.assertRegex(execute('pdfinfo', str(pdf)), r'Pages:\s+1\b')
                    text = execute('pdftotext', str(pdf), '-')
                    for label in labels:
                        self.assertIn(label, text)
            for slide in [False, True]:
                name = 'slide-host' if slide else 'a4-host'
                src, pdf = target / f'{name}.typ', target / f'{name}.pdf'
                src.write_text(host_source(slide))
                execute('typst', 'compile', str(src), str(pdf))
                info = execute('pdfinfo', str(pdf))
                self.assertRegex(info, r'Pages:\s+1\b')
                dims = re.search(r'Page size:\s+([\d.]+) x ([\d.]+)', info)
                self.assertIsNotNone(dims, info)
                for got, mm in zip(map(float, dims.groups()), (320,180) if slide else (210,297)):
                    self.assertAlmostEqual(got, mm*72/25.4, delta=.02)
                text = execute('pdftotext', str(pdf), '-')
                self.assertEqual(text.count('HOST SENTINEL'), 2)
                for label in sum(LABELS, []):
                    self.assertIn(label, text)
                result = json.loads(execute('typst', 'query', str(src), '<host-settings>', '--field', 'value'))
                self.assertEqual([v['size'] for v in result], [20,20] if slide else [10,10])
                # Extracted bounding boxes additionally catch visible host text
                # shrinking even if context introspection still looks correct.
                bbox = execute('pdftotext', '-bbox', str(pdf), '-')
                heights = [float(b)-float(a) for a,b in re.findall(r'yMin="([\d.]+)"[^>]*yMax="([\d.]+)"[^>]*>HOST</word>', bbox)]
                self.assertEqual(len(heights), 2)
                self.assertTrue(all((18<h<30) if slide else (9<h<15) for h in heights), heights)


if __name__ == '__main__':
    unittest.main()
