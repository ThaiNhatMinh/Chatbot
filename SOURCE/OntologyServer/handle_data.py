import xml.etree.ElementTree as ET
import base64
import requests
import json
import subprocess
import pathlib
path = pathlib.Path(__file__).parent.absolute()

class handleData:
    def __init__(self):
        super().__init__()

    def getAllObject(self):
        ET.register_namespace('','http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#')
        ET.register_namespace('base','http://fit.hcmus.edu.vn/ChatbotForTechniqueApp')
        ET.register_namespace('owl','http://www.w3.org/2002/07/owl#')
        ET.register_namespace('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        ET.register_namespace('xml','http://www.w3.org/XML/1998/namespace')
        ET.register_namespace('xsd','http://www.w3.org/2001/XMLSchema#')
        ET.register_namespace('rdfs','http://www.w3.org/2000/01/rdf-schema#')


        about = "http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#"

        tagOwl = '{http://www.w3.org/2002/07/owl#}'
        attrOwl = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'

        objectOwl = []
        treeOwl = ET.parse(str(path) + '/ChatbotTechnique.owl')
        for ontoTag in treeOwl.findall(tagOwl + 'NamedIndividual'):
            typeOnto = ontoTag.find(attrOwl+'type')
            if typeOnto != None and typeOnto.get(attrOwl + 'resource') == (about + "Object"):
                tmpObj = ontoTag.get(attrOwl+'about')
                obj = tmpObj.replace(about, '') 
                objectOwl.append(obj)
        return objectOwl

    def getAllAction(self):
        ET.register_namespace('','http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#')
        ET.register_namespace('base','http://fit.hcmus.edu.vn/ChatbotForTechniqueApp')
        ET.register_namespace('owl','http://www.w3.org/2002/07/owl#')
        ET.register_namespace('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        ET.register_namespace('xml','http://www.w3.org/XML/1998/namespace')
        ET.register_namespace('xsd','http://www.w3.org/2001/XMLSchema#')
        ET.register_namespace('rdfs','http://www.w3.org/2000/01/rdf-schema#')


        about = "http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#"

        tagOwl = '{http://www.w3.org/2002/07/owl#}'
        attrOwl = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'

        objectOwl = []
        treeOwl = ET.parse(str(path) + '/ChatbotTechnique.owl')
        for ontoTag in treeOwl.findall(tagOwl + 'NamedIndividual'):
            typeOnto = ontoTag.find(attrOwl+'type')
            if typeOnto != None and typeOnto.get(attrOwl + 'resource') == (about + "Operation"):
                tmpObj = ontoTag.get(attrOwl+'about')
                obj = tmpObj.replace(about, '') 
                objectOwl.append(obj)
        return objectOwl

    def import_data(self):
        ET.register_namespace('','http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#')
        ET.register_namespace('base','http://fit.hcmus.edu.vn/ChatbotForTechniqueApp')
        ET.register_namespace('owl','http://www.w3.org/2002/07/owl#')
        ET.register_namespace('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        ET.register_namespace('xml','http://www.w3.org/XML/1998/namespace')
        ET.register_namespace('xsd','http://www.w3.org/2001/XMLSchema#')
        ET.register_namespace('rdfs','http://www.w3.org/2000/01/rdf-schema#')


        about = "http://fit.hcmus.edu.vn/ChatbotForTechniqueApp#"

        tagOwl = '{http://www.w3.org/2002/07/owl#}'
        attrOwl = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'

        objectOwl = self.getAllObject()
        actionOwl = self.getAllAction()

        #xml parser
        root = ET.parse(str(path) + '/handledata/data/data.xml').getroot()
        treeOwl = ET.parse(str(path) + '/ChatbotTechnique.owl')
        rootOwl = treeOwl.getroot()

        for ontology_tag in root.findall('ontology'):
            name = ontology_tag.get('name')
            typeOnto = ontology_tag.get('type')
            whCheck = typeOnto
            if whCheck == "HOW_QUESTION": whCheck = "How"
            else: whCheck = "What"
            # print(arrName[0])
            new=ET.Element(tagOwl + 'NamedIndividual')
            new.set(attrOwl + 'about', about+name)
            newType = ET.Element(attrOwl+'type')
            newType.set(attrOwl + 'resource', about + whCheck)
            new.append(newType)

            checkProcess = False
            for objectProperty in ontology_tag.findall('objectproperty'):
                for hasBrand in objectProperty.findall('hasBrand'):
                    if hasBrand.text != None: 
                        # print(hasBrand.text)
                        newBranch = ET.Element('hasBrand')
                        newBranch.set(attrOwl+'resource', about+hasBrand.text)
                        new.append(newBranch)
                for hasContext in objectProperty.findall('hasContext'):
                    if hasContext.text != None:
                        # print(hasContext.text)
                        newContext = ET.Element('hasContext')
                        newContext.set(attrOwl+'resource',about+hasContext.text)
                        new.append(newContext)
                for hasObject in objectProperty.findall('hasObject'):
                    if hasObject.text != None:
                        # print(hasObject.text)
                        newObject = ET.Element('hasObject')
                        newObject.set(attrOwl+'resource',about+hasObject.text)
                        new.append(newObject)

                        if hasObject.text not in objectOwl:
                           
                            newRootObject = ET.Element(tagOwl + 'NamedIndividual')
                            newRootObject.set(attrOwl+'about', about + hasObject.text)
                            newROTag = ET.Element(attrOwl + 'type')
                            newROTag.set(attrOwl+'resource',about+'Object')
                            newRootObject.append(newROTag)
                            newROTag = ET.Element('hasBrand')
                            newROTag.set(attrOwl+'resource',about+'AdobePhotoshop')
                            newRootObject.append(newROTag)
                            rootOwl.append(newRootObject)
                for hasOperation in objectProperty.findall('hasOperation'):
                    if hasOperation.text != None:
                        # print(hasOperation.text)
                        newOpera = ET.Element('hasOperation')
                        newOpera.set(attrOwl+'resource',about+hasOperation.text)
                        new.append(newOpera)
                        if hasOperation.text not in actionOwl:
                            
                            newRootOpe = ET.Element(tagOwl + 'NamedIndividual')
                            newRootOpe.set(attrOwl+'about', about + hasOperation.text)
                            newROTag = ET.Element(attrOwl + 'type')
                            newROTag.set(attrOwl+'resource',about+'Operation')
                            newRootOpe.append(newROTag)
                            rootOwl.append(newRootOpe)
                for hasProcess in objectProperty.findall('hasProcess'):
                    if hasProcess.text != None:
                        # newType1 = ET.Element(attrOwl+'type')
                        # newType1.set(attrOwl + 'resource', about + 'Process')
                        # new.append(newType1)
                        checkProcess = True
                        #Thêm 1 process mới
                        newRootProcess = ET.Element(tagOwl + 'NamedIndividual')
                        newRootProcess.set(attrOwl + 'about', about+hasProcess.text)
                        newTypeProcess = ET.Element(attrOwl+'type')
                        newTypeProcess.set(attrOwl + 'resource', about + 'Process')
                        newRootProcess.append(newTypeProcess)
                        # print(hasProcess.text)
                        newProcess = ET.Element('hasProcess')
                        newProcess.set(attrOwl+'resource',about+hasProcess.text)
                        new.append(newProcess)
                for hasStep in objectProperty.findall('hasStep'):
                    stepArr = []
                    index = 1
                    for step in hasStep.findall('step'):
                        newSt = ET.Element('hasStep')
                        newSt.set(attrOwl+'resource',about+hasProcess.text+"_step"+str(index))
                        new.append(newSt)
                        newStep=ET.Element(tagOwl + 'NamedIndividual')
                        newStep.set(attrOwl + 'about', about+hasProcess.text+"_step"+str(index))
                        newStepType = ET.Element(attrOwl+'type')
                        newStepType.set(attrOwl + 'resource', about + "Task")
                        newStep.append(newStepType)
                        #newRootProcess.append(newStepType)
                        procesStep = ET.Element('hasStep')
                        procesStep.set(attrOwl+'resource',about+hasProcess.text+"_step"+str(index))
                        newRootProcess.append(procesStep)
                        for object1 in step.findall('object'):
                            if object1.text != None:
                                # print(object1.text)
                                newStepObject = ET.Element('hasObject')
                                newStepObject.set(attrOwl+'resource',about+object1.text)
                                newStep.append(newStepObject)
                        for resp in step.findall('resp'):
                            if resp.text != None:
                                # print(resp.text)
                                newStepResp = ET.Element('Response')
                                newStepResp.text = resp.text
                                newStep.append(newStepResp)
                        for hasImage in step.findall('hasImage'):
                            if hasImage.text != None:
                                # print(hasImage.text)
                                newStepImage = ET.Element('hasImage')
                                with open(str(path)+ '\\handledata\\data\\' + hasImage.text, "rb") as image_file:
                                    imageStr = base64.b64encode(image_file.read())
                                    newStepImage.text = str(imageStr) 
                                
                                newStep.append(newStepImage)
                                stepArr.append(newStep)
                        
                        index+=1
                        rootOwl.append(newStep)
            for dataProperty in ontology_tag.findall('dataproperty'):
                for Response in dataProperty.findall('Response'):
                    if Response.text != None:
                        newResp = ET.Element('Response')
                        newResp.text = Response.text
                        new.append(newResp)
                for hasVideo in dataProperty.findall('hasVideo'):
                    if hasVideo.text != None:
                        newResp = ET.Element('hasVideo')
                        newResp.text = hasVideo.text
                        new.append(newResp)
                for hasURL in dataProperty.findall('hasURL'):
                    if hasURL.text != None:
                        newResp = ET.Element('hasURL')
                        newResp.text = hasURL.text
                        new.append(newResp)
                for hasImage in dataProperty.findall('hasImage'):
                    if hasImage.text != None:
                        newResp = ET.Element('hasImage')
                        newResp.text = hasImage.text
                        new.append(newResp)

            if checkProcess == True:
                rootOwl.append(newRootProcess)

            rootOwl.append(new)
            
            # for step in stepArr:
            #     rootOwl.append(step)
            
        treeOwl.write('ChatbotTechnique.owl')
    def getData(self, data):
        # Xử lý bỏ vào file xml
        root = ET.Element('data')
        for question in data:
            ontology = ET.Element('ontology')
            #Xử lý object objectproperty
            seperate = call_API("analysis-sentence", {"sentence":question["question"]})
            print(seperate)
            ontology.set('name', seperate["title"])
            ontology.set('type', seperate["type"])

            objectProperty = ET.Element('objectproperty')

            hasBrand = ET.Element('hasBrand')
            objectProperty.append(hasBrand)
            hasContext = ET.Element('hasContext')
            objectProperty.append(hasContext)

            objectArr = seperate["object"]
            index = 0
            for obj in objectArr:
                if index < 3:
                    hasObject = ET.Element('hasObject')
                    obj = obj.split()
                    obOnto = ""
                    for ob in obj:
                        obOnto += ob+"_"
                    hasObject.text = obOnto[:-1]
                    objectProperty.append(hasObject)
                index += 1
            
            operation = seperate["action"]
            if len(operation) > 0:
                hasOperation = ET.Element('hasOperation')
                hasOperation.text = operation[0]
                objectProperty.append(hasOperation)

            #còn step chưa xử lý

            ontology.append(objectProperty)

            dataProperty = ET.Element('dataproperty')
            answer = question["anwser"]
            if len(answer["image"]) > 0:
                i = 1
                for image in answer["image"]:
                    if "http" not in image: continue
                    hasImage = ET.Element('hasImage')
                    imgName = seperate["title"] + str(i) + ".jpg"
                    i+=1
                    hasImage.text = imgName
                    dataProperty.append(hasImage)
                    with open(str(path) + "\\handledata\\data\\" + imgName, 'wb') as handle:
                        response = requests.get(image, stream=True)

                        if not response.ok:
                            print(response)

                        for block in response.iter_content(1024):
                            if not block:
                                break

                            handle.write(block)
            
            hasURL = ET.Element('hasURL')
            dataProperty.append(hasURL)
            hasVideo = ET.Element('hasVideo')
            dataProperty.append(hasVideo)

            Response = ET.Element('Response')
            Response.text = answer["answer"]

            dataProperty.append(Response)

            ontology.append(dataProperty)

            root.append(ontology)

        tree = ET.ElementTree(root)
        tree.write(str(path) + "/handledata/data" + '/data.xml', encoding="utf-8")

def call_API(_type, content):
	headers = {'Content-Type': 'application/json'}
	url = 'https://sentence-analysis.herokuapp.com/' + _type
	respone = requests.post(url, data=json.dumps(content), headers=headers)
	content = respone.json()
	list_content = content['resp']
	return list_content        

if __name__ == '__main__':
    handle = handleData()
    data = [{'question': "Can't open RAW files within Photoshop", 'anwser': {'answer': 'Try the following:1. In Photoshop go to Preferences >Camera Raw and uncheck "Use Graphics Processor"Ff that does not resolve the problem :2. In Photoshop go to Preferences > General > Reset Preferences on Quit , then close and restart Photoshop.After that, you may need to once again uncheck Preferences > Camera Raw - use graphics processorDave', 'image': []}}, {'question': 'I am new to PHOTOSHOP CC: where is the Slice tool?', 'anwser': {'answer': 'The answer has changed since this post was written in 2015. Go to Edit > Toolbar and drag it back from "Extra Tools" or you can choose Restore Defaults to put it behind the Crop tool "C".~ Jane. ', 'image': ['https://community.adobe.com/t5/image/serverpage/image-id/110645i9A56E284A7871F1F/image-size/large?v=1.0&px=999']}}, {'question': 'Problem in Photoshop: Objects are displayed twice', 'anwser': {'answer': 'Does turning off Photoshop > Preferences > Performance > Legacy Compositing and restarting Photoshop have any bearing on the issue?. ', 'image': []}}, {'question': 'Photoshop HTML Panel Events : Catch an "Undo" event.', 'anwser': {'answer': 'Try to intercept "invokeCommand" with "commandID" == 101. . ', 'image': []}}, {'question': 'Distort tool does not working', 'anwser': {'answer': 'I suspect you mean Transform >Distort..  The behaviour of transform has changed in the recent update. Where previously the shift key was used to constrain the transform , it now works the other way round and the shift key is used to unconstrain the transform.See here :New and enhanced features | Latest release of Photoshop CC Dave', 'image': []}}, {'question': 'Serious Error in latest PS update 21.2.0', 'anwser': {'answer': "It's another wonderful bug introduced by Adobe, go into preferences and disable this option if it's enabled and restart Photoshop", 'image': ['https://community.adobe.com/t5/image/serverpage/image-id/108863iECD55EB9793A70DC/image-size/large?v=1.0&px=999']}}, {'question': 'Layer glitches in PS 21.2.0', 'anwser': {'answer': "Go into preferences and disable legacy compositing if it's enabled, restart Photoshop", 'image': ['https://community.adobe.com/t5/image/serverpage/image-id/110027iF1F2240A0255A50D/image-size/large?v=1.0&px=999']}}, {'question': 'Images disappear when attempting to crop', 'anwser': {'answer': 'Reset the tool. Select the tool from the toolbar. After that, go up to the crop icon top left and left click to get the dropdown menu and click reset tool. Problem solved ', 'image': []}}, {'question': 'Photoshop 21.2 artboard gets covered with a grey screen and the the app runs slower', 'anwser': {'answer': '. Sorry that a grey box appears on the Artboard workspace in Photoshop 21.2.0 and the app is running unexpectedly slow.. Would you mind unchecking the option "Legacy compositing" from the Preferences> Performance menu in Photoshop and let us know if that helps? Also, what is your operating system and its version?. If it does not helps, try unchecking the option "use graphics processor" in the same Preferences> Performance menu and share the outcome with us.. To improve the app performance, you may checkout the steps mentioned in this article. https://helpx.adobe.com/photoshop/kb/photoshop-slow-lags.html. Thanks,Akash', 'image': []}}]
    handle.getData(data)
    handle.reTrainNLU()
    print(handle.getAllAction())
    handle.import_data()