import pathlib
import subprocess

path = pathlib.Path(".")
for mdfile in path.glob("20*.md"):
    pdffile = mdfile.with_suffix(".pdf")
    subprocess.run(["pandoc", mdfile, "-o", pdffile])
