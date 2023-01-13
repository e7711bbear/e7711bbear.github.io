#
# This script converts markdown to html
#

import markdown
import os
import re

# Params
template_file_name = "template.html"

# Clean up old HTML files except template
dir_name = "./"
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".html") and template_file_name not in item:
        os.remove(os.path.join(dir_name, item))

# Open the markdown file and parse
with open('pirates-way.md', 'r') as f:
    text = f.read()

# Validate the tags
regex = r'@#\$..*\$#@'
matches = re.findall(regex, text)
keys = []
for key in matches:
    key = key.replace('@#$', '')
    key = key.replace('$#@', '')
    keys.append(key)

print('Keys Count: %s' % len(keys))

# Counting the number of links to each tag. Should be 1 now - Subject to change.
found_error = False
for key in keys:
    key_reg = r'(#%s)' % key
    keys_matches = re.findall(key_reg, text)
    match_count = len(keys_matches)
    if match_count != 1:
        found_error = True
        print("Error: key %s has %s link tags" % (key, match_count))

if found_error:
    # We found a problem with the keys we stop.
    exit(0)

# Changing the links to future pages

key_reg = r']\(#..*\)'
matches = re.findall(key_reg, text)
for match in matches:
    new_link = match.replace('](#', '](./')
    new_link = new_link.replace(')', '.html)')
    text = text.replace(match, new_link)

# Building the pages
pages = text.split('@#$')

print('Pages to be created: %s' % len(pages))

# Open the template file
template_html = ''
with open(template_file_name, 'r') as f:
    template_html = f.read()

index = 0
for index, page in enumerate(pages):
    # extract the page key
    page_key = ''
    if index == 0:
        page_key = 'index'
    else:
        regex = r'^..*\$#@'
        match = re.findall(regex, page)
        page_key = match[0].replace('$#@', '') # removing the end of the key
    # Look up previous and next keys
    previous_key = None
    next_key = None
    if index == 0:
        next_key = keys[0]
    else:
        index = 0
        count = len(keys)
        for index, key in enumerate(keys):
            if key == page_key:
                if index > 0:
                    previous_key = keys[index-1]
                if index < count-1:
                    next_key = keys[index + 1]

    # Trim off to only have the page md
    if index == 0:
        page_md = page
    else:
        page_partitions = page.partition('$#@')
        page_md = page_partitions[2]
    page_html = markdown.markdown(page_md)
    # Additional replace
    page_html = page_html.replace('[pagebreak]', '<div id=\'pagebreak\'></div>')

    # Insert content in template
    final_page_html = template_html.replace('[[INSERT_PLUG]]', page_html)

    # Insert previous and next links
    previous_link = ''
    if previous_key is not None:
        previous_link = '<a href="./%s.html">Previous</a>' % previous_key
    elif index != 0:
        previous_link = '<a href="./index.html">Previous</a>'
    final_page_html = final_page_html.replace('[[PREVIOUS]]', previous_link)

    next_link = ''
    if next_key is not None:
        next_link = '<a href="./%s.html">Next</a>' % next_key
    final_page_html = final_page_html.replace('[[NEXT]]', next_link)

    # write end-result to final file
    filename = '%s.html' % page_key
    with open(filename, 'w') as f:
        print("Writing %s" % filename)
        f.write(final_page_html)


