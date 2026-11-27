import sys
src=open('build_pdf.py').read()
upto=sys.argv[1] if len(sys.argv)>1 else None
if upto: src=src.split(upto)[0]
src+="\npdf.close()\nprint('pages done')\n"
exec(compile(src,'build_pdf.py','exec'))
