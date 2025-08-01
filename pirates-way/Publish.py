#
# This script converts markdown to html
#

import markdown
import os
import re
import sys
import getopt

# Params
allow_book_content = False
book_format = False

## Parsing the command line params
opts, args = getopt.getopt(sys.argv[1:],"h",["allow_book_content","book_format"])
for opt, arg in opts:
  if opt == '-h':
     print ('publish.py --allow_book_content --book_format')
     sys.exit()
  elif opt in "--allow_book_content":
     allow_book_content = True
  elif opt in "--book_format":
     book_format = True

if book_format:
    template_file_name = "book_template.html"
else:
    template_file_name = "web_template.html"

print("Starting Publishing job with params:")
print("Template File: %s" % template_file_name)
print("Book Content: %s" % allow_book_content)
print("Book Format: %s" % book_format)
print("---")

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
book_keys = []
for key in matches:
    key = key.replace('@#$', '')
    key = key.replace('$#@', '')
    if "|book_only|" not in key: # Exclude the content that is book only
        keys.append(key)
    else:
        key = key.replace('|book_only|', '')
        if allow_book_content is False: # if book content is not allowed, we quarantine it
            book_keys.append(key)
        else:
            keys.append(key)

print('Keys Count: %s' % len(keys))
print('Book Exclusive Keys Count: %s' % len(book_keys))

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
    key_in_link = match.replace('](#', '')
    key_in_link = key_in_link.replace(')', '')

    # If book only, we do no links
    if key_in_link in book_keys:
        text = text.replace(match, ']()')
    else:
        new_link = match.replace('](#', '](./')
        new_link = new_link.replace(')', '.html)')
        text = text.replace(match, new_link)

# Building the pages
pages = text.split('@#$')
page_count = 0
if book_format:
    book_html = ""

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
    # We don't gen the pages that are book only here
    page_key = page_key.replace('|book_only|', '') # in case it has the modifier
    if page_key in book_keys:
        continue

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

    # Replaces that should happen before html conversion
    page_md = page_md.replace('[<->]', '&harr;')

    page_html = markdown.markdown(page_md, extensions=['tables'])

    page_components = page_md.partition('\n')
    page_title = None
    if page_components[2][0] == '#':
        title_piece = page_components[2].partition('\n')[0]
        page_title = title_piece.replace('# ', '')
        page_title = page_title.replace('#', '')
    # Setting the page title if available
    if page_title is not None:
        page_template_html = template_html.replace('[pagetitle]', page_title)
    else:
        page_template_html = template_html.replace('[pagetitle]', 'How to build tech products and the teams behind them')

    # Additional replace
    page_html = page_html.replace('[pagebreak]', '<div id=\'pagebreak\'></div>')

    ## -- Emoji replace
    page_html = page_html.replace('📖', '&#x1F4D6;')
    page_html = page_html.replace('🛋', '&#x1F6CB;')
    page_html = page_html.replace('✅', '&#9989;')
    page_html = page_html.replace('⭐', '&#11088;')
    page_html = page_html.replace('⬜', '&#9634;')


    # Insert content in template
    final_page_html = page_template_html.replace('[[INSERT_PLUG]]', page_html)

    if book_format is False: # Web version
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

        redirect_html = """<!DOCTYPE html>
        <html>
        <head>
          <meta http-equiv="refresh" content="0; url=https://arnaud.works/" />
          <title>Redirecting...</title>
        </head>
        <body>
          <p>The Pirate Way is now a book with updated content making this page obseleted.!<br/>If you are not redirected in 5 seconds, <a href="https://arnaud.works/">click here</a>.</p>
        </body>
        </html>
        """

        final_page_html = redirect_html
        # write end-result to final file
        filename = '%s.html' % page_key
        with open(filename, 'w') as f:
            print("Writing %s" % filename)
            f.write(final_page_html)
            page_count += 1

    else:
        book_html += final_page_html

if book_format:
    # write end-result to final file
    filename = '__book.html'
    with open(filename, 'w') as f:
        print("Writing %s" % filename)
        f.write(book_html)
        page_count += 1

print('Pages created: %s' % page_count)


