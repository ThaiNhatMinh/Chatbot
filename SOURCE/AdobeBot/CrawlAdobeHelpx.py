# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import bs4
import logging
from html.parser import HTMLParser
from html import unescape

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("CrawAdobeHelpx")
logger.setLevel(logging.DEBUG)
parser = HTMLParser()
def normalize_string(string):
    string = str(string)
    new_str = string.strip()
    new_str = new_str.replace('\n', ' ')
    new_str = unescape(new_str)
    return new_str

class HelpXContent(object):

    def __init__(self, title):
        self.title = title
        self.contents = []
    def add(self, content):
        self.contents.append(("text", content))
    def add_image(self, url):
        self.contents.append(("image", url))
    def add_video(self, url):
        self.contents.append(("video", url))
        
    def is_empty(self):
        return len(self.contents) == 0

WEB_TUTORIAL = 'tutorial-content'
WEB_ARTICLE = 'main-content'
ADOBEHELPX_URL = 'https://helpx.adobe.com'

def update_image_url(text):
    soup = BeautifulSoup(text, "html.parser")
    imgs = soup.findAll('img')
    for img in imgs:
        image_path = img.get('src')
        if image_path and image_path.startswith('/'):
            img['src'] = ADOBEHELPX_URL + image_path
    return str(soup)


def get(url):

    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    if str(url).find("/how-to/") != -1:
        main = soup.findAll('div', attrs={'class': WEB_TUTORIAL}, limit=1)
        main = main[0].section
    else:
        main = soup.findAll('div', attrs={'id': WEB_ARTICLE}, limit=1)
        main = main[0].findAll('div', recursive=False)[1]

    contents = []
    current = None
    for child in main.children:
        if type(child) is bs4.element.NavigableString:
            continue
        if len(child.contents) == 1 and child.contents[0] == '\n':
            continue
        if child['class'][0] == 'header':
            header = normalize_string(child.div.contents[1].contents[0])
            if current is not None and not current.is_empty():
                    # logger.info("Part: {} is empty, {}".format(current.title, len(current.contents)))
                contents.append(current)
            logger.info(u"Add header: {}\n".format(header))
            current = HelpXContent(header)
        elif child['class'][0] == 'image' and current is not None:
            current.add_image(ADOBEHELPX_URL + child.div.img['src'])
            logger.info("Add image: " + ADOBEHELPX_URL + child.div.img['src'] + '\n')
        elif child['class'][0] == 'text':
            text = ''
            # logger.info("p: {}".format(''.join(child.div.contents)))
            # continue
            text_element = child.findAll('div', attrs={'class': 'text'}, limit=1)[0]
            for element in text_element.contents:
                if element.name == 'p':
                    text = text + normalize_string(element.contents[0])
                elif element.name == 'ul' or element.name == 'ol':
                    for li in element.contents:
                        if type(li) is bs4.element.NavigableString:
                            continue
                        if len(li.contents) == 1:
                            text = text + normalize_string(li.contents[0])
                        elif len(li.contents) > 1:
                            text = text + " ".join(str(c) for c in li.contents)
                else:
                    logging.error("Unknow tag: {}, content: '{}'".format(element.name, element))
            # for p in child.div.contents:
            #     if type(p) is bs4.element.NavigableString:
            #         continue
            #     if type(p.contents[0]) is bs4.element.Tag:
            #         text = text + str(p.contents[0])
            #     elif p.name == 'p':
            #         text = text + normalize_string(p.contents[0])
            #     elif p.name == 'ul' or p.name == 'ol':
            #         for li in p.contents:
            #             if type(li) is bs4.element.NavigableString:
            #                 continue
            #             if len(li.contents) == 1:
            #                 text = text + normalize_string(li.contents[0])
            #             elif len(li.contents) > 1:
            #                 text = text + " ".join(str(c) for c in li.contents)
            text = update_image_url(normalize_string(text))
            logger.info("Add text: {}\n".format(text))
            if current is None:
                current = HelpXContent("Introduction")
            current.add(text)
        elif child['class'][0] == 'variable':
            text = "{}: {}".format(child.contents[7].p.span.contents[0], normalize_string(child.contents[8].p.p.contents[0]))
            # for p in child.contents:
            #     logger.info("p: {}".format(p))
            logger.info("Add variable: {}\n".format(text))
            current.add(text)
        elif child['class'][0] == 'procedure':
            logger.info('Add procedure')
            current.add(str(child.div))
            # logger.info(str(child.div.ol, encoding="utf-8"))
            logger.info(child.div.ol.prettify(encoding="utf-8"))
        elif child['class'][0] == 'video':
            # logger.info(child.contents[3])
            title = child.contents[1].contents[0]
            url_video = child.contents[5].iframe['src']
            logger.info('Add video: title: {}, URL: {}'.format(title, url_video))
            current.add_video(url_video)
        elif child['class'][0] == 'learn-header':
            learn_header = normalize_string(child.p.contents[0])
            logger.info("Add learn header: {}".format(learn_header))
            if current is not None and not current.is_empty():
                    # logger.info("Part: {} is empty, {}".format(current.title, len(current.contents)))
                contents.append(current)
            current = HelpXContent(learn_header)
        elif child['class'][0] == 'learn-video':
            url_video = child.div.iframe['src']
            logger.info("Add learn video: {}".format(url_video))
            if current is None:
                current = HelpXContent("Video tutorial")
            current.add_video(url_video)
    else:
        if current is not None and not current.is_empty():
            contents.append(current)
    return contents
    # logger.info(type(child))

def to_string(content: HelpXContent) -> str:

    return "".join(content.contents)

if __name__ == '__main__':
    url = ['https://helpx.adobe.com/photoshop-elements/using/creating-layers.html',
    'https://helpx.adobe.com/photoshop/using/choosing-colors.html',
    'https://helpx.adobe.com/photoshop/using/color-settings.html',
    'https://helpx.adobe.com/photoshop/how-to/camera-raw.html',
    'https://helpx.adobe.com/photoshop/how-to/ps-basics-fundamentals.html',
    'https://helpx.adobe.com/photoshop/using/create-smart-objects.html',
    'https://helpx.adobe.com/photoshop/key-concepts/composite.html',
    'https://helpx.adobe.com/photoshop/how-to/compositing.html']

    # for u in url:
    #     get(u)
    get(url[1])