import xml.etree.ElementTree as ET
import base64
import requests
import json
import threading
from train import train_nlu, train_dialogue

import pathlib
path = pathlib.Path(__file__).parent.absolute()

class handleData:
    def __init__(self):
        super().__init__()

    def importToNLU(self, data):
        # Xử lý bỏ vào file .md
        whatQues = []
        howQues = []
        for question in data:
            seperate = call_API("analysis-sentence", {"sentence":question["question"]})
            if seperate["type"] == "WHAT_QUESTION": 
                data = {
                    "question":question["question"],
                    "object":seperate["object"],
                }
                whatQues.append(data)
            else: 
                data = {
                    "question":question["question"],
                    "object":seperate["object"],
                    "operation":seperate["action"],
                }
                howQues.append(data)
 
        with open(str(path) + "/data/nlu_data.md", 'r', encoding="utf-8") as f:
            contents = f.readlines()

        i = 0
        whatindex = 0
        howindex = 0
        for line in contents:
            if line == "## intent:what_object\n" and len(whatQues) > 0:
                
                whatindex = i
            if line == "## intent:ask_how\n" and len(howQues) > 0:
                
                howindex = i
            i+=1

        if whatindex > 0: 
            whatStr = self.generateWhat(whatQues)
            contents[whatindex] += whatStr
        if howindex > 0:
            howStr = self.generateHow(howQues)
            contents[howindex] += howStr

        with open(str(path) + "/data/nlu_data.md", 'w', encoding="utf-8") as file:
            file.writelines(contents)        
        

        
    def generateWhat(self, data):
        formWhat = [
            "\n- what is the [] ?\n",
            "- what is [] ?\n",
            "- please tell me about the [].\n",
            "- I dont know the []. Can you help me ?\n",
            "- I dont know what is the []. Can you help me ?\n",
            "- tell me about the [].\n",
            "- whats the [] ?\n",
            "- whats [] ?\n",
            "- []\n\n",
        ]
        resp = ""
        
        for dt in data:
            userQues = dt["question"]
            usIndx = 1
            for obj in dt["object"]:
                if usIndx < 3:
                    userQues = userQues.replace(obj, "[" + obj + "]" + "(object_" + str(usIndx) + ")")
                    usIndx+=1
            resp += "- " + userQues
            objStr = ""
            objIndex = 1
            for obj in dt["object"]:
                if objIndex < 3:
                    objStr += "[" + obj + "]" + "(object_" + str(objIndex) + ") "
                    objIndex+=1
            for form in formWhat:
                resp += form.replace("[]", objStr[:-1])   

        return resp

    def generateHow(self, data):
        formHow = [
            "\n- how to () the [] ?\n",
            "- () the []\n",
            "- how do I () the [] ?\n",
            "- i dont know how to () the [] ?\n",
            "- tell me the way to () the [] ?\n",
            "- tell me how to () the [] ?\n",
            "- show me the way to () the [] ?\n",
            "- show me how to () the [] ?\n",
            "- is there any way to () the [] ?\n\n",
        ]

        resp = ""
        
        for dt in data:
            userQues = dt["question"]
            usIndx = 1
            for obj in dt["object"]:
                if usIndx < 4:
                    userQues = userQues.replace(obj, "[" + obj + "]" + "(object_" + str(usIndx) + ")")
                    usIndx+=1
            if len(dt["operation"]) > 0:
                userQues = userQues.replace(dt["operation"][0], "[" + dt["operation"][0] + "]" + "(action)")

            resp += "- " + userQues

            objStr = ""
            opeStr = ""
            objIndex = 1
            for obj in dt["object"]:
                if objIndex < 4:
                    objStr += "[" + obj + "]" + "(object_" + str(objIndex) + ") "
                    objIndex+=1
            if len(dt["operation"]) > 0:
                opeStr += "[" + dt["operation"][0] + "]" + "(action),"
            for form in formHow:
                resp += form.replace("[]", objStr[:-1]).replace("()", opeStr)
                
        return resp

    def importToStory(self, data):
        #read index
        with open(str(path) + "/data/stories.md", 'r') as file:
            contents = file.readlines()
        
        count = 1
        for line in contents:
            if "## story_" in line: count += 1

        whatQues = []
        howQues = []
        for question in data:
            seperate = call_API("analysis-sentence", {"sentence":question["question"]})
            if seperate["type"] == "WHAT_QUESTION": 
                data = {
                    "question":question["question"],
                    "object":seperate["object"],
                }
                whatQues.append(data)
            else: 
                data = {
                    "question":question["question"],
                    "object":seperate["object"],
                    "operation":seperate["action"],
                }
                howQues.append(data)

        formWhat = '* what_object{}\n\t- slot{}\n\t- action_confirm\n\t- action_search_entity\n\t- action_renew\n\n'
        formHow = '* ask_how{}\n\t- action_confirm\n\t- action_search_how_answer\n\t- action_show_process\n\t- action_renew\n\t- restart\n\n'
        
        for what in whatQues:
            ind = 1
            objStr = ''
            for obj in what["object"]:
                if ind < 3:
                    objStr += '"object_' + str(ind) + '":"' + obj + '",'
                    ind+=1
            with open(str(path) + "/data/stories.md", 'a') as file:
                file.write("## story_" + str(count).zfill(5) + '\n' + formWhat.replace("{}", '{' + objStr[:-1] + '}'))
                count+=1

        for how in howQues:
            ind = 1
            objStr = ''
            if len(how["operation"]) > 0:
                objStr += '"action":"' + how["operation"][0] + '",'
            for obj in how["object"]:
                if ind < 4:
                    objStr += '"object_' + str(ind) + '":"' + obj + '",'
                    ind += 1
            with open(str(path) + "/data/stories.md", 'a') as file:
                file.write("## story_" + str(count).zfill(5) + '\n' + formHow.replace("{}", '{' + objStr[:-1] + '}'))
                count += 1
        

    def reTrainNLU(self):
        print("retrain")
        # subprocess.call([str(path) + '/retrain_nlu.bat'])
        # subprocess.call([str(path) + '/retrain_dialog.bat'])
        train_nlu()
        print("Retrain NLU Done.")
        train_dialogue()
        print("Retrain Dialog Done.")


def call_API(_type, content):
	headers = {'Content-Type': 'application/json'}
	url = 'https://sentence-analysis.herokuapp.com/' + _type
	respone = requests.post(url, data=json.dumps(content), headers=headers)
	content = respone.json()
	list_content = content['resp']
	return list_content        

if __name__ == '__main__':
    handle = handleData()
    handle.reTrainNLU()
    # data = [{'question': 'Select and Mask tools not working in Photoshop CC 2020 21.2.0 on macOS', 'anwser': {'answer': '(I think) I fixed it by going into Preferences and resetting all preferences. After I did that I was able to start selecting in the Select and Mask task space again.', 'image': []}}, {'question': 'GPU Not showing in Performance settings after updating Photoshop to version 21.2', 'anwser': {'answer': "It's an issue with version 21.2 and I have reported herehttps://feedback.photoshop.com/photoshop_family/topics/bug-in-photoshop-version-21-2-not-detecting-older-gpusAdobe are looking. into the issue and hopefully will provide a fix in the next update", 'image': []}}]
    # # data = [{'question': "Can't open RAW files within Photoshop", 'anwser': {'answer': 'Try the following:1. In Photoshop go to Preferences >Camera Raw and uncheck "Use Graphics Processor"Ff that does not resolve the problem :2. In Photoshop go to Preferences > General > Reset Preferences on Quit , then close and restart Photoshop.After that, you may need to once again uncheck Preferences > Camera Raw - use graphics processorDave', 'image': []}}, {'question': 'I am new to PHOTOSHOP CC: where is the Slice tool?', 'anwser': {'answer': 'The answer has changed since this post was written in 2015. Go to Edit > Toolbar and drag it back from "Extra Tools" or you can choose Restore Defaults to put it behind the Crop tool "C".~ Jane. ', 'image': ['https://community.adobe.com/t5/image/serverpage/image-id/110645i9A56E284A7871F1F/image-size/large?v=1.0&px=999']}}, {'question': 'Problem in Photoshop: Objects are displayed twice', 'anwser': {'answer': 'Does turning off Photoshop > Preferences > Performance > Legacy Compositing and restarting Photoshop have any bearing on the issue?. ', 'image': []}}, {'question': 'Photoshop HTML Panel Events : Catch an "Undo" event.', 'anwser': {'answer': 'Try to intercept "invokeCommand" with "commandID" == 101. . ', 'image': []}}, {'question': 'Distort tool does not working', 'anwser': {'answer': 'I suspect you mean Transform >Distort..  The behaviour of transform has changed in the recent update. Where previously the shift key was used to constrain the transform , it now works the other way round and the shift key is used to unconstrain the transform.See here :New and enhanced features | Latest release of Photoshop CC Dave', 'image': []}}, {'question': 'Serious Error in latest PS update 21.2.0', 'anwser': {'answer': "It's another wonderful bug introduced by Adobe, go into preferences and disable this option if it's enabled and restart Photoshop", 'image': ['https://community.adobe.com/t5/image/serverpage/image-id/108863iECD55EB9793A70DC/image-size/large?v=1.0&px=999']}}, {'question': 'Layer glitches in PS 21.2.0', 'anwser': {'answer': "Go into preferences and disable legacy compositing if it's enabled, restart Photoshop", 'image': ['https://community.adobe.com/t5/image/serverpage/image-id/110027iF1F2240A0255A50D/image-size/large?v=1.0&px=999']}}, {'question': 'Images disappear when attempting to crop', 'anwser': {'answer': 'Reset the tool. Select the tool from the toolbar. After that, go up to the crop icon top left and left click to get the dropdown menu and click reset tool. Problem solved ', 'image': []}}, {'question': 'Photoshop 21.2 artboard gets covered with a grey screen and the the app runs slower', 'anwser': {'answer': '. Sorry that a grey box appears on the Artboard workspace in Photoshop 21.2.0 and the app is running unexpectedly slow.. Would you mind unchecking the option "Legacy compositing" from the Preferences> Performance menu in Photoshop and let us know if that helps? Also, what is your operating system and its version?. If it does not helps, try unchecking the option "use graphics processor" in the same Preferences> Performance menu and share the outcome with us.. To improve the app performance, you may checkout the steps mentioned in this article. https://helpx.adobe.com/photoshop/kb/photoshop-slow-lags.html. Thanks,Akash', 'image': []}}]
    # # handle.getData(data)
    # handle.importToNLU(data)
    # handle.reTrainNLU()
    # print(handle.getAllAction())
    # handle.import_data()