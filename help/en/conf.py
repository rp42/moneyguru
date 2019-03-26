REPLACEMENTS = {
    'cmd': u'Ctrl+',
    'cmd_opt': u'Ctrl+Alt+',
    'cmd_shift': u'Ctrl+Shift+',
}

REPLACEMENT_STR = u'\n'.join([u'.. |%s| replace:: %s' % (key, value) for key, value in REPLACEMENTS.items()])

rst_epilog = REPLACEMENT_STR
master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'sphinxdoc'
html_domain_indices = False
html_use_index = False
html_show_sourcelink = False
