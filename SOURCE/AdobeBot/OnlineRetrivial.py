import requests
import json
import logging
import SimilarityModel
import CrawlAdobeHelpx

KEY = 'f9ee0ed0-cbd4-11ea-9c95-555571ca657c'
ADOBEHELPX_URL = 'https://helpx.adobe.com'
YOUTUBE_URL = "https://www.youtube.com/"

def get_document(url):
    headers = {'Content-Type': 'application/json'}
    parser_url = "http://parser.rtechs.net/api/parser"
    content = {"link": url}
    try:
        resp = requests.post(parser_url, data = json.dumps(content), headers=headers)
    except Exception as expression:
        logging.error("Failed to parse web content at {}".format(url))
        logging.error(expression)
        return None
    if resp.status_code == 200:
        return resp.json()['result']["contents"][0]["paragraphs"]
    else:
        logging.info("Failed to parse content at url: {}, status code: {}, content: {}"
            .format(url, resp.status_code, resp.content))
        return None

def get_urls(query):
    headers = { 'apikey': KEY }
    params = (("q",query),)
    logging.info(query)
    response = requests.get('https://app.zenserp.com/api/v2/search', headers=headers, params=params)
    if response.status_code != 200:
        logging.info("Failed to search online: {}".format(response.status_code))
        logging.info(response.content)
        return None
    data = response.json()
    urls = []
    # Get link of the article:
    # ...
    if not (data.get('featured_snippet') is None):
        url = data["featured_snippet"]["url"]
        urls.append(url)
        #description = data["featured_snippet"]["description"]
    elif not (data["organic"][0].get("url") is None):
        url = data["organic"][0]["url"]
        urls.append(url)
    elif data["organic"][0].get('video') is not None:
        url = data["organic"][0]["videos"][0]["url"]
        urls.append(url)
    else:
        for res in data["organic"]:
            if res.get('url') is not None:
                url = res['url']
                urls.append(url)
    return urls

def endcode(contents):
    result = []
    for content in contents:
        if content[0] == 'text':
            result.append({'respone': content[1]})
        elif content[0] == 'video':
            result.append({'video': [
                {'res_video': 'I have found a video about that may help you:'}, {'link': content[1]}]})
        elif content[0] == 'image':
            result.append({'image': content[1]})
        else:
            result.append({'respone': content[1]})
    return result

def search_for(query):
    ''' Search over the internet 'text'.
        Get link of the article.
        Get content of the article.
        Check similarity between text and content of the article.

        @return tuple result for web and ontology
    '''
    # Search over the internet 'text':
    # ...
    urls = get_urls(query)
    if len(urls) == 0:
        logging.error("Can not search over internet")
        return None

    query = query.lower()
    query = query.split('adobe photoshop')[0] # Remove 'adobe photoshop', it is not helpful for similar checking

    for url in urls:
        # Get content of the article:
        logging.info("URL: " + url)
        if url.startswith(YOUTUBE_URL):
            result = [{'video': [
                {'res_video': 'I have found a video about that may help you:'}, {'link': url}]}]
            return [json.dumps(result), json.dumps(result)]

        documents = []
        if url.startswith(ADOBEHELPX_URL) and not query.startswith("what is"):
            contents = CrawlAdobeHelpx.get(url)
            if contents is None:
                continue
            num_video = 0
            video_content = None
            for content in contents:
                print(content.title)
                documents.append(content.title)
                for c in content.contents:
                    if type(c) is tuple and c[0] == 'video':
                        num_video = num_video + 1
                        video_content = content
            # If there is one video from tutorial, return directly
            if num_video == 1 and url.find("/how-to/") != -1:
                result = endcode(video_content.contents)
                return [json.dumps(result), json.dumps(result)]
        else:
            documents = get_document(url)
            if documents is None or len(documents) == 0:
                continue

        # Check similarity between text and content of the article.
        lsi = SimilarityModel.LSIModel(documents, num_topics=len(documents))
        lsi_sim = lsi.similarity(query)
        logging.info("Similarity information:")
        for i, sim in lsi_sim:
            logging.info("({}, {})".format(i, sim))

        result = documents[lsi_sim[0][0]]

        if url.startswith(ADOBEHELPX_URL) and not query.startswith("what is"):
            result_for_web = endcode(contents[lsi_sim[0][0]].contents)
        else:
            result_for_web = [{'respone': documents[lsi_sim[0][0]]}]
        result_for_ontology = [{'question': query,
                                'answer':
                                {
                                    'answer': result,
                                    'image': []
                                }}
                            ]
        return [json.dumps(result_for_web), json.dumps(result_for_ontology)]
