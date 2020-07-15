from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
#from bot import AdobeAPI
import requests
import json
from rasa_core.events import AllSlotsReset
from rasa_core.events import Restarted
import random
import time
from nltk.stem import WordNetLemmatizer 
from nltk.stem import PorterStemmer
import logging
import OnlineRetrivial

import spacy
import neuralcoref

ps = PorterStemmer()
lemmatizer = WordNetLemmatizer() 

story = []
statement = []

def getRandomFromFile(filename):
	lines = open(filename).read().splitlines()
	myline =random.choice(lines)
	return myline

class ActionSearchEntity(Action):
	def name(self):
		return 'action_search_entity'
	
	def run(self, dispatcher, tracker, domain):
		time_1 = time.time()
		respone = ''
		link_video = ''
		image = ''
		res = []
		list_entity = []
		context = []

		story.append(tracker.latest_message.get('text'))
		current_state = tracker.current_state()
		msg = current_state.get('latest_message', {}) 
		story.append(msg)

		version = next(tracker.get_latest_entity_values("version"), None)
		
		_objects_1 = tracker.get_slot("object_1")
		_objects_2 = tracker.get_slot("object_2")
		_link = tracker.get_slot("link")
		#04062020
		_mention = tracker.get_slot("mention")
		if _mention is not None:
			nlp = spacy.load('en_core_web_sm')
			neuralcoref.add_to_pipe(nlp, greedyness=0.52)
			if len(statement) > 0:
				conversation = statement[len(statement)-1]+ '. ' + tracker.latest_message.get('text') + '.'
				doc = nlp(conversation)
				print(doc)
				if(doc._.coref_clusters != []):
					cluster = doc._.coref_clusters[-1].mentions[-1]._.coref_cluster.main
					print('cluster: ' + format(cluster))
					if _objects_1 is None:
						_objects_1 = format(cluster)

					if _objects_1 != format(cluster) and _objects_2 is None:
						_objects_2 = format(cluster)
			else:
				dispatcher.utter_message("[{'respone': 'I don't know what object you mention.'}]")
				return []
		else:
			statement.append(tracker.latest_message.get('text'))
			print(statement)
		if _objects_1 is not None:
			print('obj1_what: ' + _objects_1)
			query = 'What is ' + _objects_1
			if _objects_1 == 'camera raw':
				_objects_1 = _objects_1.title()
				_objects_1 = ''.join(_objects_1.split())
			else:
				_objects_1 = _objects_1.replace(' ','_')
				_objects_1 = _objects_1.capitalize()
			list_entity.append(_objects_1)			

			if _link is not None:
				query+= ' ' + _link
			if _objects_2 is not None:
				query += ' ' + _objects_2
				print('obj2_what: ' + _objects_2)
				if _objects_2 == 'camera raw':
					_objects_2 = _objects_2.title()
					_objects_2 = ''.join(_objects_2.split())
				else:
					_objects_2 = _objects_2.replace(' ','_')
					_objects_2 = _objects_2.capitalize()
				list_entity.append(_objects_2)	
		if version is not None:
			context.append(version.upper())
		logging.info("text: {}".format(tracker.latest_message.get('text')))
		logging.info("list_entity: {}".format(" ".join(list_entity)))
		if not list_entity:
			document = OnlineRetrivial.search_for(tracker.latest_message.get('text'))
			if not document:
				dispatcher.utter_message("[{'respone': 'Sorry I dont know that'}]")
			else:
				dispatcher.utter_message(document[0])
			return []
			
		else:
			data = {'entity': list_entity, 'context': context}

			list_content = call_API('ask_what', data)
			if format(list_content) == "[['Type', []]]" :
				#03062020
				query += ' Adobe Photoshop'
				if version is not None:
					query += ' ' + (version.upper())
				doc = OnlineRetrivial.search_for(query)
				if doc:
					dispatcher.utter_message(doc[0])
				else:
					dispatcher.utter_message("[{'respone': 'Sorry I dont know that'}]")
				return []
			else:
				#list_content = content['resp']
				temp = []
				for item in list_content:
					if item[0] == 'Type':
						if len(item[1]) > 1:
							temp = item[1]

				#print(len(temp))
				if len(temp) > 1:
					res.append({'type': temp})
					dispatcher.utter_message(format(res))
					return []
				else:
					for item in list_content:
						if item[0] == 'Video':
							link_video = item[1]
						elif item[0] == 'Response':
							respone = item[1]
						elif item[0] == 'Image':
							image = item[1]

					video_respone = getRandomFromFile("file.txt")
					confirm = tracker.get_slot("confirm")

					if respone is not "":
						res.append({"confirm": confirm})
						res.append({"respone" : respone})
					if link_video is not "":
						video_list = []
						video_list.append({"res_video": video_respone})
						video_list.append({"link": link_video})
						res.append({"video" : video_list})
					if image is not "":
						res.append({"image": image})
					#print('have response')
					dispatcher.utter_message(format(res))

					time_2 = time.time()
					#print(time_2 - time_1)
					return []

class ActionShowProcess(Action):
	def name(self):
		return 'action_show_process'
	
	#define all actions need.
	def run(self, dispatcher, tracker, domain):
		time_1 = time.time()
		process = tracker.get_slot("list_process")
		steps = []
		#print(process)
		story.append(tracker.latest_message.get('text'))
		current_state = tracker.current_state()
		msg = current_state.get('latest_message', {}) 
		story.append(msg)
		#print(len(entities))
		# đợi Ly check lại => chỗ này sửa thành nếu lenghth = 1 thì call API lấy steps
		if not process:
			dispatcher.utter_message("[{'respone': 'I don't have knowledge about this, you can check on our forum: https://forums.adobe.com/community/photoshop'}]")
		else:
			res = [{"process": process}]
			dispatcher.utter_message(format(res))
			time_2 = time.time()
			print(time_2 - time_1)
		return []


class ActionShowSteps(Action):
	def name(self):
		return 'action_show_steps'
	
	#define all actions need.
	def run(self, dispatcher, tracker, domain):
		#from rasa_core.actions.action import ACTION_LISTEN_NAME
		time_1 = time.time()
		steps = [] 
		respone = ''
		link_video = ''
		image = ''
		res = []
		#dispatcher.utter_message("Wait a few mins")
		process = tracker.latest_message.get('text')
		story.append(tracker.latest_message.get('text'))
		current_state = tracker.current_state()
		msg = current_state.get('latest_message', {}) 
		story.append(msg)
		#print(entities)
		#process = process.title()
		process = process.replace(' ','_')
		print(process)
		process_name = {'process': process}
		content = call_API('ask_step', process_name)
		#print(content)
		for item in content:
			if item[0] == 'Video':
				link_video = item[1]
			elif item[0] == 'Respone':
				respone = item[1]
			elif item[0] == 'Step':
				steps = item[1]
			elif item[0] == 'Image':
				image = item[1]

		if respone is not "":
			res.append({"respone" : respone})
		if link_video is not "":
			res.append({"video": link_video})
		if steps:
			res.append({"step": steps})
		if image is not "":
			res.append({"image": image})

		if res:
			dispatcher.utter_message(format(res))
		else:
			dispatcher.utter_message("[{'respone': 'I don't have knowledge about this, you can check on our forum: https://forums.adobe.com/community/photoshop'}]")
		
		time_2 = time.time()
		print(time_2 - time_1)
		return []

class ActionSearchHowAnswer(Action):
	def name(self):
		return 'action_search_how_answer'
	
	#define all actions need.
	def run(self, dispatcher, tracker, domain):
		time_1 = time.time()
		list_entity = []
		operator = []
		context = []
		confirm = tracker.get_slot("confirm")
		story.append(tracker.latest_message.get('text'))	
		
		version = (tracker.get_slot("version"))
		if version is not None:
			context.append(version.upper())

		os = (tracker.get_slot("OS"))
		if os is not None:
			os = os.title()
			os = ''.join(os.split())
			context.append(os)

		equipment = (tracker.get_slot("equipment"))
		if equipment is not None:
			equipment = equipment.title()
			equipment = ''.join(equipment.split())
			context.append(equipment)

		action = tracker.get_slot("action")

		if action is not None:
			query = 'How to '+ action
			#action = ps.stem(action)
			action = action.title()
			action = action.split()
			for op in action:
				if op != 'And':
					operator.append(op)

		obj_1 = next(tracker.get_latest_entity_values("object_1"), None)
		obj_2 = next(tracker.get_latest_entity_values("object_2"), None)
		obj_3 = next(tracker.get_latest_entity_values("object_3"), None)
		_link = next(tracker.get_latest_entity_values("link"), None)
		_link2 = next(tracker.get_latest_entity_values("link_2"), None)

		#04062020
		_mention = tracker.get_slot("mention") 
		if _mention is not None:			
			nlp = spacy.load('en_core_web_sm')
			neuralcoref.add_to_pipe(nlp, greedyness=0.52)
			if len(statement) > 0: 
				conversation = statement[len(statement)-1]+ '. ' + tracker.latest_message.get('text') + '.'			
				doc = nlp(conversation)
				print(doc)
				if(doc._.coref_clusters != []):
					cluster = doc._.coref_clusters[-1].mentions[-1]._.coref_cluster.main			
					print('cluster: ' + format(cluster))
					if obj_1 is None:
						obj_1 = format(cluster)
						 
					if obj_1 != format(cluster) and obj_2 is None:
						obj_2 = format(cluster)
					if obj_1 != format(cluster) and obj_2 != format(cluster) and obj_3 is None:
						obj_3 = format(cluster)
			else:
				dispatcher.utter_message("[{'respone': 'I don't know what object you mention.'}]")
				return []

		else:
			statement.append(tracker.latest_message.get('text'))
			print(statement)
		if obj_1 is not None:
			query += ' '+ obj_1
			print('obj1_how: ' + obj_1)
			if obj_1.lower() == 'camera raw' or obj_1.lower() == 'toolbox' :
				obj_1 = obj_1.title()
				obj_1 = ''.join(obj_1.split())
				list_entity.append(obj_1)

			else:
				obj_1 = obj_1.title()
				obj_1 = obj_1.split()
				for item in obj_1:
					list_entity.append(item)
		
		#obj_2 = tracker.get_slot("object_2")
		if _link is not None:
			query += ' '+ _link
		if obj_2 is not None:
			query += ' '+ obj_2
			print('obj2_how: ' + obj_2)
			if obj_2.lower() == 'camera raw' or obj_2.lower() == 'toolbox':
				obj_2 = obj_2.title()
				obj_2 = ''.join(obj_2.split())
				list_entity.append(obj_2)
			else:
				obj_2 = obj_2.replace(" ","_")
				obj_2 = obj_2.capitalize()
				obj_2 = obj_2.split()
				for item in obj_2:
					list_entity.append(item)
		if _link2 is not None:
			query += ' '+ _link2
		if obj_3 is not None:
			query += ' '+ obj_3
			print('obj3_how: ' + obj_3)
			if obj_3.lower() == 'camera raw' or obj_3.lower() == 'toolbox':
				obj_3 = obj_3.title()
				obj_3 = ''.join(obj_3.split())
				list_entity.append(obj_3)
			else:
				obj_3 = obj_3.replace(" ","_")
				obj_3 = obj_3.capitalize()
				obj_3 = obj_3.split()
				for item in obj_3:
					list_entity.append(item)
		
		list_process = [] # array process
		steps = [] # array steps
		respone = ''
		link_video = ''
		image = ''
		res = []
		data = {'operator': operator,'entity': list_entity, 'context': context}
		#print(operator)
		#print(list_entity)
		if operator != [] and list_entity != []:
			list_content = call_API('ask_how', data)
			
			# if not list_content:
			# 	context = []
			# 	list_content.clear()
			# 	data = {'operator': operator,'entity': list_entity, 'context': context}
			# 	list_content = call_API('ask_how', data)
			if list_content:
				for item in list_content:		
					if item[0] == 'Process':
						list_process = item[1]
					elif item[0] == 'Video':
						link_video = item[1]
					elif item[0] == 'Respone':
						respone = item[1]
					elif item[0] == 'Step':
						steps = item[1]
					elif item[0] == 'Image':
						image = item[1]

				#dispatcher.utter_message(content['resp'])
			video_respone = getRandomFromFile("file.txt")
			if respone is not "":
				res.append({"confirm": confirm})
				res.append({"respone" : respone})
			if list_process:
				res.append({"process" : list_process})
			if link_video is not "":
				video_list = []
				video_list.append({"res_video": video_respone})
				video_list.append({"link": link_video})
				res.append({"video" : video_list})
			if steps:
				res.append({"step" : steps})
			if image is not "":
				res.append({"image" : image})

			if not res:
				#05062020
				query += ' Adobe Photoshop'
				if version is not None:
					query += ' ' + version.upper()
				doc = OnlineRetrivial.search_for(query)
				if doc is not None:
					logging.info(doc)
					dispatcher.utter_message(doc[0])
					# dispatcher.utter_message(format(res))
				else:
					dispatcher.utter_template("utter_find_object", tracker)
				time_2 = time.time()
				print(time_2 - time_1)
				return []
			else:
				dispatcher.utter_message(format(res))
				time_2 = time.time()
				print(time_2 - time_1)
				return [SlotSet("list_process", list_process)]
		else:
			dispatcher.utter_message("[{'respone': 'I don't have knowledge about this, you can check on our forum: https://forums.adobe.com/community/photoshop'}]")
			time_2 = time.time()
			print(time_2 - time_1)
			return []


class ActionRenew(Action): 	
	def name(self): 		
		return 'action_renew' 

	def run(self, dispatcher, tracker, domain): 
		return_slots = []
		#print(tracker.slots[0])
		for slot in tracker.slots:
			if tracker.slots[slot] != None:
				#print(tracker.slots[slot])
				return_slots.append(SlotSet(slot, None))

		file = open("history.txt", "a")
		file.write("Story \n")
		for item in story:
			file.write(str(item) + "\n")
		story.clear()
		file.write("\n")
		file.close()
		
		return return_slots

class ActionRestart(Action):
    def name(self):
        return "restart"

    def run(self, dispatcher, tracker, domain):
        # do something here
        return [Restarted()]

class ActionDefaultFallback(Action):

   def name(self):
      return "action_default_fallback"

   def run(self, dispatcher, tracker, domain):
   		story.append(tracker.latest_message.get('text'))
   		current_state = tracker.current_state()
   		msg = current_state.get('latest_message', {})
   		story.append(msg)
   		dispatcher.utter_message("[{'respone': 'Sorry, I dont understand...'}]")

class ActionConfirm(Action):
    def name(self):
        return "action_confirm"

    def run(self, dispatcher, tracker, domain):
        entity_1 = tracker.get_slot("entity_1")
        entity_2 = tracker.get_slot("entity_2")
        action = tracker.get_slot("action")
        object_1 = tracker.get_slot("object_1")
        object_2 = tracker.get_slot("object_2")
        object_3 = tracker.get_slot("object_3")
        version = tracker.get_slot("version")
        os = tracker.get_slot("OS")
        confirm = ''
        equipment = tracker.get_slot("equipment")
        if entity_1 != None and entity_2 != None:
        	confirm = 'You want to know about '+entity_1+' '+ entity_2
        elif entity_1 != None:
        	confirm = 'You want to know about '+entity_1
        
        if action != None and object_1 != None:
        	confirm = 'You want to know about ' +action+ ' ' +object_1
        if action != None and object_1 != None and version != None:
        	confirm = 'You want to know about '+action+' '+object_1+' in '+version
        if action != None and object_1 != None and object_2 != None:
         	confirm = 'You want to know about '+action+' '+object_1+' in '+object_2
        if action != None and object_2 != None:
         	confirm = 'You want to know about '+action+' '+object_2
        if action != None and object_1 != None and object_2 != None and object_3 != None:
        	confirm = 'You want to know about '+action+' '+object_1+' in '+object_2+' '+object_3
       	if action != None and object_1 != None and object_2 != None and version != None:
         	confirm = 'You want to know about '+action+' '+object_1+' '+object_2+' in '+version
        if action != None and object_2 != None and version != None:
        	confirm = 'You want to know about '+action+' '+object_2+' in '+version
       	if action != None and object_1 != None and equipment != None:
        	confirm = 'You want to know about '+action+' '+object_1+' on '+equipment
        if action != None and object_1 != None and equipment != None and version != None:
         	confirm = 'You want to know about '+action+' '+object_1+' in '+version+' on '+equipment
        if action != None and object_1 != None and os != None and version != None:
         	confirm = 'You want to know about '+action+' '+object_1+' in '+version+' in '+os

        return [SlotSet("confirm", confirm)]


def call_API(_type, content):
	headers = {'Content-Type': 'application/json'}
	url = 'http://localhost:5000/' + _type
	respone = requests.post(url, data = json.dumps(content), headers = headers)
	content = respone.json()
	list_content = content['resp']
	return list_content




