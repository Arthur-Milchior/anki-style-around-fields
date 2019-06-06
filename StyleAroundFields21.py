# -*- coding: utf-8 -*-
# Copyright: Arthur Milchior arthur@milchior.fr
# encoding: utf8
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Feel free to contribute to this code on https://github.com/Arthur-Milchior/anki-style-around-fields
# Add-on number 12287769 https://ankiweb.net/shared/info/631147309

import re
from anki.notes import Note
from aqt.utils import tooltip, showWarning, askUser
import aqt
from aqt import mw
from aqt.qt import *
from aqt.clayout import CardLayout
from anki.hooks import addHook

flag = re.MULTILINE | re.DOTALL
def debug(p):
    pass

def mustacheToSpan(text, clean=False):
    """adding a span tag with class equal to its name for each mustache.

    Replace a potential span already here
    """
    def editMustache(matchobj):
        """third element of the group is enclosed in Mustache mustache
        and span.

        The class of the span and the name of the condition are the 2nd element
        of the group. The first element being the kind of condition to use."""

        (name)=matchobj.group(1) or matchobj.group(2)
        r=("" if clean else "<span SpanField='mustache' class='"+name+"'>" )+"{{"+name+"}}"+("" if clean else "</span>")
        debug(f"Calling editMustache({matchobj})={r}")
        return r
    baseRegexp= r"{{([^#^/}][^}]*)}}"
    extendedRegexp = r"<span SpanField='mustache' class='([^#^'>]*)'>\s*{{\1}}\s*</span>"
    regexp = extendedRegexp+r"|"+baseRegexp
    text=re.sub(regexp,editMustache,text,flags=flag)
    debug(f"Calling mustacheToSpan({text},{clean})=text")
    return text

def runModel(model, clean=False):
    for tmpl in model['tmpls']:
        for key in ["afmt","qfmt","bafmt","bqfmt"]:
            if key in tmpl and tmpl[key]:
                template = tmpl[key]
                if template:
                    newTemplate = mustacheToSpan(template,clean=clean)
                ask = "Change \n"+template+"\n-----------------\nto:\n-----------------\n"+newTemplate
                #                if askUser(ask):
                tmpl[key]=newTemplate
                # else:
                #     showWarning("meta mentionned which do(es) not exists: "+str(s)+".")
                #     raise
    mm=mw.col.models
    mm.save(model)
    mm.flush()


def runBrowser(browser, clean=False):
    nids=browser.selectedNotes()
    mids = set()
    for nid in nids:
        note = mw.col.getNote(nid)
        mid = note.mid
        if mid not in mids:
            mids.add(mid)
            model=mw.col.models.get(mid)
            runModel(model,clean=clean)



def setupMenu(browser):
    browser.form.menuEdit.addSeparator()

    a = QAction("Style around fields", browser)
    a.triggered.connect(lambda : runBrowser(browser))
    browser.form.menuEdit.addAction(a)

    a = QAction("Remove style around fields", browser)
    a.triggered.connect(lambda : runBrowser(browser,clean=True))
    browser.form.menuEdit.addAction(a)

addHook("browser.setupMenus", setupMenu)
