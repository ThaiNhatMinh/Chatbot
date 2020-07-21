import requests
import json
import logging
import SimilarityModel
import CrawlAdobeHelpx

KEY = '00ee0320-c84c-11ea-9fb3-3d967eb895f9'
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

def search_for(query):
    ''' Search over the internet 'text'.
        Get link of the article.
        Get content of the article.
        Check similarity between text and content of the article.

        @return tuple result for web and ontology
    '''
    # Search over the internet 'text':
    # ...
    headers = { 'apikey': KEY }
    params = (("q",query),)
    logging.info(query)
    response = requests.get('https://app.zenserp.com/api/v2/search', headers=headers, params=params)
    if response.status_code != 200:
        logging.info("Failed to search online: {}".format(response.status_code))
        logging.info(response.content)
        return None
    data = response.json()
    # Get link of the article:
    # ...
    if not (data.get('featured_snippet') is None):
        url = data["featured_snippet"]["url"]
        #description = data["featured_snippet"]["description"]
    elif not (data["organic"][0].get("url") is None):
        url = data["organic"][0]["url"]
    else:
        url = data["organic"][0]["videos"][0]["url"]
    # Get content of the article:
    logging.info("URL: " + url)
    if url.startswith(YOUTUBE_URL):
        result = [{'video': [
            {'res_video': 'I have found a video about that may help you:'}, {'link': url}]}]
        return [json.dumps(result), json.dumps(result)]

    documents = []
    if url.startswith(ADOBEHELPX_URL):
        contents = CrawlAdobeHelpx.get(url)
        if contents is None:
            return None
        for content in contents:
            print(content.title)
            documents.append(content.title)
    else:
        documents = get_document(url)
        if documents is None:
            return None

    # Check similarity between text and content of the article.
    lsi = SimilarityModel.LSIModel(documents, num_topics=len(documents))
    lsi_sim = lsi.similarity(query)
    logging.info("Similarity information:")
    for i, sim in lsi_sim:
        logging.info("({}, {})".format(i, sim))

    result = documents[lsi_sim[0][0]]

    if url.startswith(ADOBEHELPX_URL):
        result_for_web = []
        for content in contents[lsi_sim[0][0]].contents:
            if content[0] == 'text':
                result_for_web.append({'respone': content[1]})
            elif content[0] == 'image':
                result_for_web.append({'image': content[1]})
            else:
                result_for_web.append({'respone': content[1]})
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
