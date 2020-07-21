import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from handle_data import handleData
import requests
import json

import pathlib
path = pathlib.Path(__file__).parent.absolute()

class crawlPtsComunity:
   def __init__(self, url):
      #Lấy thời gian cũ trong file dữ liệu
      fH = open(str(path) + "\\handledata\\crawl-history.txt", "r")
      Ltime = fH.read()
      fH.close()
      self.lastTime = datetime.strptime(Ltime, '%b %d %Y')
      options = Options()
      options.add_argument('--headless')
      options.add_argument('--disable-gpu')
      options.add_argument('--disable-application-cache')
      browser = webdriver.Chrome(chrome_options=options)
      
      # browser = webdriver.Firefox()
      if "https://community.adobe.com/t5/photoshop/bd-p" in url:
         browser.get("https://community.adobe.com/t5/photoshop/bd-p/photoshop?page=1&sort=latest_replies&filter=all")

      browser.get(url)
      time.sleep(3)
      page = browser.page_source

      browser.quit()
      self.soup = BeautifulSoup(page, 'html.parser')
   
   def get_link_to_array(self):
      previewCard = self.soup.find_all("div", {"class":"preview-card__translate-container"})
      # print(previewCard)
      link = []
      for card in previewCard:
         check = True#card.find("span", {"class":"userStrip__correct-answer-text"})
         # check = card.find("div", {"class":"community-page-reply community-page-reply-desktop-view"})
         if check != None:
            question = card.find("a").getText()
            seperate = call_Sen_API("check-wh-question", {"sentence":question})
            if seperate == "WHAT_QUESTION" or seperate == "HOW_QUESTION":
               link.append(card.find("a")['href'])
      return link

   def get_anwser(self):
      data = {}
      dataAnwser = {
         "answer":"",
         "image":[]
      }
      time = self.soup.find("span",{"class":"user-strip-timestamp spectrum-Body5"})
      if time.getText() == "an hour ago" or "minutes" in time.getText():
         date_time_obj = datetime.now() - timedelta(hours=1)
      else: 
         if "hours ago" in time.getText():
            date_time_obj = datetime.now() - timedelta(hours=int(time.getText()[0]))
         else:
            date_time_obj = datetime.strptime(time.getText(), '%b %d, %Y')
      if date_time_obj < self.lastTime:
         #Ghi log time vào file history
         curTime = datetime.now().strftime("%b %d %Y")
         fH = open(str(path) + "\\handledata\\crawl-history.txt", "w")
         fH.write(curTime)
         fH.close()
         return "DONE";
      question = self.soup.find("div", {"class":"lia-message-subject"})
      anwser = self.soup.find("div",{"class":"correct-answer-div"})
      # Nếu có câu trả lời
      if anwser != None:
         div = anwser.find("div", {"class":"spectrum-grid-row spectrum-grid-middle-xs content"})
         if div != None:
            pArr = div.find_all("p")
            for p in pArr:
               if p.find("img") != None:
                  dataAnwser["image"].append(p.find("img")["src"])
               anwserTxt = p.getText().replace("\xa0",". ")
               if "Hi" in anwserTxt: continue
               dataAnwser["answer"] += anwserTxt
         dataAnwser["answer"] = dataAnwser["answer"].replace('"','')
         questionTxt = question.getText()
         questionTxt = questionTxt.replace("\n","")
         questionTxt = questionTxt.replace("\r","")
         questionTxt = questionTxt.replace("\t","")
         data["question"] = questionTxt
         data["anwser"] = dataAnwser
      # Nếu là bài hướng dẫn thì lấy có step
      return data

   def getListQuestion(self):
      previewCard = self.soup.find_all("div", {"class":"preview-card__translate-container"})
      # print(previewCard)
      link = []
      for card in previewCard:
         question = card.find("a").getText()
         link.append(question)
      
      fH = open(str(path) + "\\handledata\\question.txt", "a", encoding="utf-8")
      for ques in link:
         fH.write(ques + "\n")
      fH.close()

      return "Done"

def call_API(_type, content):
	headers = {'Content-Type': 'application/json'}
	url = 'http://localhost:5000/' + _type
	respone = requests.post(url, data=json.dumps(content), headers=headers)
	content = respone.json()
	list_content = content['resp']
	return list_content

def call_Sen_API(_type, content):
	headers = {'Content-Type': 'application/json'}
	url = 'https://sentence-analysis.herokuapp.com/' + _type
	respone = requests.post(url, data=json.dumps(content), headers=headers)
	content = respone.json()
	list_content = content['resp']
	return list_content

def call_API_Reload(_type, content):
	headers = {'Content-Type': 'application/json'}
	url = 'http://localhost:5000/' + _type
	respone = requests.get(url)

	return respone

def get_Data_Func():
   # time.sleep(31536000)
   baseurl = "https://community.adobe.com"
   first = "/t5/photoshop/bd-p/photoshop?page="
   second = "&sort=latest_replies&filter=resolved"
   i = 0
   dataQuestion = []
   while True:
      i += 1
      page = crawlPtsComunity(baseurl + first + str(i) + second)

            # page.get_site_info()
      links = page.get_link_to_array()
      print(links)
      checkDone = False
      if len(links) > 0:
         for link in links:
            pageLink = crawlPtsComunity(baseurl + link)
            print(pageLink.get_anwser())
            answer = pageLink.get_anwser()
            if answer == "DONE":
               checkDone = True
               print("Dừng")
               break
            dataQuestion.append(answer)
      if checkDone:
         break

   if len(dataQuestion) > 0:
      handle = handleData()
      handle.importToNLU(dataQuestion)
      handle.importToStory(dataQuestion)
      call_API('import-data', dataQuestion)
      call_API_Reload('reload')
      handle.reTrainNLU()
		# call to ontology get data
   
      

if __name__ == '__main__':

   print("Worker crawl data for adobot...")
   while True:
      time.sleep(2592000)
      get_Data_Func()

