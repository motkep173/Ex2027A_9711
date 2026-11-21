"""Build the figures: figures/NAME.tex (a standalone TikZ picture) -> figures/NAME.pdf and figures/NAME.svg.

The booklets include the PDF (\\qfig{NAME}); the site embeds the SVG. Both are committed, so the
GitHub Action does not need to build them. Run after adding or changing a figure:
    python3 tools/build_figures.py            # all figures whose .tex is newer than the .pdf/.svg
    python3 tools/build_figures.py --all
"""
import glob, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(HERE, 'figures')


def stale(tex):
    base = tex[:-4]
    return any(not os.path.exists(base + ext) or os.path.getmtime(base + ext) < os.path.getmtime(tex)
               for ext in ('.pdf', '.svg'))


def build(tex):
    name = os.path.basename(tex)[:-4]
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                            '-output-directory', tmp, tex], capture_output=True, text=True)
        pdf = os.path.join(tmp, name + '.pdf')
        if r.returncode or not os.path.exists(pdf):
            sys.exit(f'{tex}: xelatex failed\n' + r.stdout[-2000:])
        shutil.copy(pdf, os.path.join(FIG, name + '.pdf'))
        subprocess.run(['pdftocairo', '-svg', pdf, os.path.join(FIG, name + '.svg')], check=True)
    print('built', name)


def main():
    texs = sorted(glob.glob(os.path.join(FIG, '*.tex')))
    for tex in texs:
        if '--all' in sys.argv or stale(tex):
            build(tex)


if __name__ == '__main__':
    main()
