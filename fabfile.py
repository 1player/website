import os
from fabric.api import local
import livereload

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, 'output')

def _makePelican():

    conf = os.path.join(ROOT, 'pelicanconf.py')

    return 'pelican -s %s -o %s' % (conf, OUTPUT)

def _makeTheme():
    static = os.path.join(ROOT, 'themes/combo/static')
    src = os.path.join(static, 'less/style.less')
    out = os.path.join(static, 'style.css')

    return 'lessc %s %s' % (src, out)

def dev(port=8000):
    local(_makePelican())
    local(_makeTheme())

    os.chdir(OUTPUT) 
    server = livereload.Server() 

    server.watch('../content/*', _makePelican())
    server.watch('../content/pages/*', _makePelican())
    server.watch('../themes/combo/templates/*', _makePelican())
    server.watch('../themes/combo/static/less/*', 
        livereload.shell(_makeTheme()))
    server.watch('../themes/combo/static/*.css', _makePelican())

    server.watch('*.html')
    server.watch('*.css')
    server.serve(liveport=35729, port=port)