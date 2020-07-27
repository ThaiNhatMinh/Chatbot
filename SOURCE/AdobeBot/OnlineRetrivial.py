import requests
import json
import logging
import SimilarityModel
import CrawlAdobeHelpx
from handle_data import handleData
# from actions import call_API

KEY = '2d3aa670-cf60-11ea-871e-f7a573154db6'
ADOBEHELPX_URL = 'https://helpx.adobe.com'
YOUTUBE_URL = "https://www.youtube.com/"


cache_results = {}
handler = handleData()

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

def call_API(_type, content):
    headers = {'Content-Type': 'application/json'}
    url = 'http://localhost:5000/' + _type
    respone = requests.post(url, data = json.dumps(content), headers = headers)
    content = respone.json()
    list_content = content['resp']
    return list_content

def save_cache(query, result):
    cache_results[query] = [json.dumps(result), json.dumps(result)]
    # "answer": "bcd",
    #         "video": "b",
    #         "image": [],
    #         "step": [
    #             {
    #                 "resp": "def",
    #                 "image": []
    #             }
    #         ]
    data = {
        "question": query,
        "anwser": {}
    }

    if len(result) == 1:
        if result[0][0] == 'video':  # One video
            data['answer']['video'] = result[0][1][1]['link']
        else:
            data['answer']['answer'] = result[0][1]
    elif len(result) >= 2:
        data['answer']['step'] = []
        for part in result:
            if part[0] == 'respone':
                data['answer']['step'].append({'resp': part[1]})
            elif part[0] == 'image':
                data['answer']['step'].append({'image': part[1]})
            elif part[0] == 'video':
                data['answer']['video'] = result[0][1][1]['link']

    handler.importToNLU([data])
    handler.importToStory([data])
    # call_API('import-online', [data])

def search_for(query):
    ''' Search over the internet 'text'.
        Get link of the article.
        Get content of the article.
        Check similarity between text and content of the article.

        @return tuple result for web and ontology
    '''
    origin_query = query

    for cache_query, cache_result in cache_results.items():
        if query == cache_query:
            logging.info("Found result in cache, return now...")
            return cache_result
    # Search over the internet 'text':
    # ...
    urls = get_urls(query)
    if urls is not None and len(urls) == 0:
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
            cache_results[origin_query] = [json.dumps(result), json.dumps(result)]
            return cache_results[origin_query]

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
                cache_results[origin_query] = [json.dumps(result), json.dumps(result)]
                return cache_results[origin_query]
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
        cache_results[origin_query] = [json.dumps(result_for_web), json.dumps(result_for_ontology)]
        return cache_results[origin_query]
