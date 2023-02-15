from http.client import MULTI_STATUS
import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def md_to_html(text):
    """
    My highly ameteur attempt for the optional Markdown to HTML Conversion
    part of the specifications.. please be kind!
    """
    # for titles
    titles = re.findall(r'^\s{0,3}#{1,6}\s+.+', text, re.MULTILINE)
    for title in titles:
        pre = re.search(r'\s{0,3}#+\s+(?=.+)', title)
        pre = pre.group()
        pre_removed = title.replace(pre, '')
        if pre.count('#') == 1:
            title_m = "<h1>" + pre_removed.rstrip() + "</h1>"
            text = text.replace(title, title_m, 1)
        elif pre.count('#') == 2:
            title_m = "<h2>" + pre_removed.rstrip() + "</h2>"
            text = text.replace(title, title_m, 1)
        elif pre.count('#') == 3:
            title_m = "<h3>" + pre_removed.rstrip() + "</h3>"
            text = text.replace(title, title_m, 1)
        elif pre.count('#') == 4:
            title_m = "<h4>" + pre_removed.rstrip() + "</h4>"
            text = text.replace(title, title_m, 1)
        elif pre.count('#') == 5:
            title_m = "<h5>" + pre_removed.rstrip() + "</h5>"
            text = text.replace(title, title_m, 1)
        elif pre.count('#') == 6:
            title_m = "<h6>" + pre_removed.rstrip() + "</h6>"
            text = text.replace(title, title_m, 1)


    # for bold texts
    s_bolds = re.findall(r'\*\*+\S+[\w\W]+?\S+\*\*+', text)
    for match in s_bolds:
        s_bold_m = '<b>' + match[2:len(match) - 2] + '</b>'
        text = text.replace(match, s_bold_m, 1)

    u_bolds = re.findall(r'\A__+\S+[\w\W]+?\S+__+|\s+?__+\S+[\w\W]+?\S+__+', text)
    for match in u_bolds:
        if '<b>' not in match and '</b>' not in match:
            u_bold_m = '<b>' + match[3:len(match) - 2] + '</b>'
            text = text.replace(match, u_bold_m, 1)

    # for unordered list
    list_items = re.findall(r'((^[-*] .*\n*)+)+', text, re.MULTILINE)
    for i in range(len(list_items)):
        items = re.findall('^[-*] .*', list_items[i][0], re.MULTILINE)
        items_m = []
        for item in items:
            item_m = '<li>' + item[2: ].strip() + '</li>'
            items_m.append(item_m)
        lists = '<ul>' + ''.join(items_m) + '</ul>'
        text = text.replace(list_items[i][0], lists)

    # for links
    links = []
    linkswithtexts = re.findall(r'\[+[^\]]*\]+\(+[^\)]*\)+', text)
    for match in linkswithtexts:
        textpart = re.search(r'(?<=\[)[^\[\]]+(?=\]+)', match)
        linkpart= re.search(r'(?<=\]\().*(?=\))', match)
        if textpart:
            link = f'<a href="{linkpart.group()}">{textpart.group()}</a>'
            links.append(link)
            text = text.replace(match, link, 1)

    raw_links = re.findall(r'https?://[^\s\)]*[A-Za-z0-9~$^+.=]', text)
    for match in raw_links:
        if not {i for i in links if match in i} and f'<a href="{match}"'  not in text:
            link = f'<a href="{match}">{match}</a>'
            text = text.replace(match, link, 1)


    # for paragraphs
    paragraphs = re.finditer(r'((?:[^\n][\n\r]{0,3})+)', text, re.MULTILINE)

    add_right = 0
    for paragraph in paragraphs:
        titles = re.findall(r'^\n*<h\d>.+?</h\d>\n*', paragraph.group(), re.MULTILINE)
        tlists = re.findall(r'^(<ul>(<li>.+?</li>\n*?\r*?)+</ul>)', paragraph.group(), re.MULTILINE)
        lists = []
        for i in tlists:
            a = i[0]
            lists.append(a)
        titles_n_lists = titles + lists
        titles_n_lists.sort(key=lambda i:paragraph.group().index(i))
        item_count = 0
        endpos = 0
        if len(titles_n_lists) > 0:

            for item in titles_n_lists:
                item_escaped = re.compile(re.escape(item))
                this_item = item_escaped.search(text, paragraph.start() + add_right)
                item_count += 1
                if item == titles_n_lists[0]:
                    if this_item.start() > paragraph.start() + add_right  and paragraph.end() + add_right > this_item.end():
                        text = text[ : paragraph.start() + add_right] + '<p>' + text[paragraph.start() + add_right: this_item.start()] + '</p>' + text[this_item.start(): this_item.end()] + '<p>' + text[this_item.end(): ]
                        add_right += 10
                        endpos = this_item.end() +10

                        if item_count == len(titles_n_lists):
                            text = text[ : paragraph.end() + add_right] + '</p>' + text[paragraph.end() + add_right: ]
                            add_right += 4
                    elif this_item.start() > paragraph.start() + add_right:
                        text = text[ : paragraph.start() + add_right] + '<p>' + text[paragraph.start() + add_right: this_item.start()] + '</p>' + text[this_item.start(): ]
                        add_right += 7
                        endpos = this_item.end() + 7

                    elif paragraph.end() + add_right > this_item.end():
                        text = text[:this_item.end()] + '<p>' + text[this_item.end(): ]
                        add_right += 3
                        endpos = this_item.end() + 3

                        if item_count == len(titles_n_lists):
                            text = text[ : paragraph.end() + add_right] + '</p>' + text[paragraph.end() + add_right: ]
                            add_right += 4


                else:
                    if this_item.start() > endpos + 2 and paragraph.end() + add_right > this_item.end():
                        print(endpos)
                        text = text[: this_item.start()] + '</p>' + text[this_item.start(): this_item.end()] + '<p>' + text[this_item.end(): ]
                        add_right += 7

                        endpos = this_item.end() + 7
                        if item_count == len(titles_n_lists):
                            text = text[: paragraph.end() + add_right] + '</p>' + text[paragraph.end() + add_right: ]
                            add_right += 4

                    elif paragraph.end() + add_right > this_item.end():
                        text = text[: this_item.start() - 4] + text[this_item.start() : this_item.end()] + '<p>' + text[this_item.end(): ]
                        endpos = this_item.end() - 1
                        add_right += -1
                        if item_count == len(titles_n_lists):
                            text = text[: paragraph.end() + add_right] + '</p>' + text[paragraph.end() + add_right: ]
                            endpos = this_item.end() + 4
                            add_right += 4


        else:
            text = text[ : paragraph.start() + add_right] + '<p>' + text[paragraph.start() + add_right: paragraph.end() + add_right] + '</p>' + text[paragraph.end() + add_right:]
            add_right += 7


    return text


