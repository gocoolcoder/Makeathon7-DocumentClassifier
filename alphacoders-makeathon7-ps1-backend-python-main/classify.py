from pdf2image import convert_from_path
import base64
import requests
import json
from google.cloud import vision
import cv2
import glob
import re
from shutil import rmtree,copy
import os
import numpy as np
import requests

#Endpoint to fetch all the processed documents details
API_ENDPOINT = "http://localhost:3000/api/documents"

#Function to send image and fetch data from the Google Vision API
def vision(image_path,detection_type):
    with open(image_path, 'rb') as image_file:
        content_json_obj = {
               'content': base64.b64encode(image_file.read()).decode('UTF-8')
        }
        content = image_file.read()
    feature_json_obj = []
    request_list = []
    feature_json_obj.append({
                   'type': detection_type,
                   'maxResults': 10,
           })
    request_list.append({
           'features': feature_json_obj,
           'image': content_json_obj,
    })
    data = {}
    data["requests"] = request_list
    response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=AIzaSyDIMeUNReYT4tP3Ul0iY6cbyjg-aAIHLGs',data=json.dumps(data),headers={'Content-Type': 'application/json'})
    return json.loads(response.text)['responses'][0]['textAnnotations']

#functionality to extract data from each partitions using vision and logics
def extraction(ocr_bits):
    invoice_flag = 1
    order_flag = 1
    order = None
    invoice = None
    for bits in ocr_bits:
        if("invoice" in bits.lower() and "order" in bits.lower() and (invoice_flag==1 or order_flag==1)):
            valid_list = [item for item in (bits.replace(" "," \n").replace("\n"," \n").split('\n')) if item.strip().isdigit() and len(item.strip()) > 5]
            if(len(valid_list)>1):
                invoice_flag = 0
                order_flag = 0
                if(bits.lower().find("invoice")<bits.lower().find("order")):
                    invoice = valid_list[0].strip()
                    order = valid_list[1].strip()
                else:
                    invoice = valid_list[1].strip()
                    order = valid_list[0].strip()
        elif(("order" in bits.lower() or "po" in bits.lower()) and (invoice_flag==1 or order_flag==1)):
            valid_list = [item for item in (bits.replace(" "," \n").replace("\n"," \n").split('\n')) if item.strip().isdigit() and len(item.strip()) >= 5]
            if(len(valid_list)>0):
                order_flag = 0
                order = valid_list[0].strip()
        elif("invoice " in bits.lower() and (invoice_flag==1 or order_flag==1)):
            valid_list = [item for item in (bits.replace(" "," \n").replace("\n"," \n").split('\n')) if item.strip().isdigit() and len(item.strip()) >= 5]
            if(len(valid_list)>0):
                invoice_flag = 1
                invoice = valid_list[0].strip()
    return order,invoice

#functionality to extract quantities present in each document
def extract_quantity(image,contents,file_name):
    for i in range(1,len(contents)):
        data = contents[i]["description"]
        if "qty" in data.lower() or "quantity" in data.lower():
            if("qty" in data.lower()):
                factor = 3
            else:
                factor = .5
            vert = contents[i]["boundingPoly"]["vertices"]
            y1,y2,x1,x2 = min(vert[0]['x'],vert[2]['x']),max(vert[0]['x'],vert[2]['x']),min(vert[0]['y'],vert[2]['y']),max(vert[0]['y'],vert[2]['y'])
            width = y2-y1
            height = x2-x1
            #x1 = max(x1-height*2,0)
            x2 = image.shape[0]
            y1 = max(y1-int(width*factor),0)
            y2 = min(y2+int(width*factor),image.shape[1])
            dirName = "./assets/quantity/"
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            cv2.imwrite('./assets/quantity/'+file_name+'_qty.jpg',img_resize(image[x1:x2,y1:y2],800))
    raw = vision('./assets/quantity/'+file_name+'_qty.jpg','TEXT_DETECTION')
    raw = raw[0]['description']
    valid_list = [item for item in (raw.replace(".","").replace(",","").split('\n')) if item.strip().isdigit()]
    print(valid_list)
    quantity = 0 
    for qty in valid_list:
        quantity+=int(qty)
    return quantity,valid_list

#functionality  to clean image for the extraction of data for quantity calculation
def img_resize(img,scale):
    scale_percent = scale # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
#     resized = cv2.fastNlMeansDenoisingColored(resized,None,10,10,7,21)
    kernel = np.ones((7,7),np.uint8)
#     dilation = cv2.dilate(resized,kernel,iterations = 1)
    erosion = cv2.erode(resized,kernel,iterations = 2)
    opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    return closing

#Main function to classify all the documents
def classify(files):
    counter = 0
    response = []
    for pdf in files:  
        counter += 1        
        file_name = pdf.split("/")[-1].split(".")[0]
        print("--------------------------------------")
        print("Processing " + str(counter) +"/"+ str(len(files)) +" files -- " + file_name + " ...")
        print("--------------------------------------")
        pages = convert_from_path(pdf, 200)
        masterDirName = "./assets/splits"+ "/" + file_name
        if not os.path.exists(masterDirName):
            os.makedirs(masterDirName)
        else:
            rmtree(masterDirName)
            os.makedirs(masterDirName)
        for index in range(len(pages)):
            pages[0].save(masterDirName+'/pdf_img_'+file_name+'.jpg', 'JPEG')
        print("Process 1/4 : Extracting data from pdf")
        for file in glob.glob(masterDirName+'/*.jpg'):
            try:
                contents = vision(file,'TEXT_DETECTION')
                dirName = "./assets/ocr_bits" + "/" + file_name
                if not os.path.exists(dirName):
                    os.makedirs(dirName)
                else:
                    rmtree(dirName)
                    os.makedirs(dirName)

                image = cv2.imread(file)

                print("Process 2/4 : Creating partitions from extracted data")
                for i in range(1,len(contents)):
                    data = contents[i]["description"]
                    if "order" in data.lower() or "po" in data.lower() or "invoice" in data.lower():
                        vert = contents[i]["boundingPoly"]["vertices"]
                        y1,y2,x1,x2 = min(vert[0]['x'],vert[2]['x']),max(vert[0]['x'],vert[2]['x']),min(vert[0]['y'],vert[2]['y']),max(vert[0]['y'],vert[2]['y'])
                        width = y2-y1
                        height = x2-x1
                        #x1 = max(x1-height*2,0)
                        x2 = min(x2+height*4,image.shape[0])
                        y1 = max(y1-width*2,0)
                        y2 = min(y2+width*4,image.shape[1])
                        cv2.imwrite(dirName+'/part'+str(i)+'.jpg',image[x1:x2,y1:y2])
                print("Process 3/4 : Extracting Data from OCR Partitions")
                ocr_bits = []
                for file in glob.glob(dirName + './*.jpg'):
                    content = vision(file,'TEXT_DETECTION')
                    ocr_bits.append(content[0]['description'])
                order , invoice = extraction(ocr_bits)
                tag = None
                if(order != None):
                    if(invoice != None):
                        dirName = "./assets/results/orders/" + str(order) + "/" +str(invoice)
                        tag = "invoice"
                    else:
                        dirName = "./assets/results/orders/" + str(order)
                        tag = "order"
                    if not os.path.exists(dirName):
                        os.makedirs(dirName)
                    copy(pdf, dirName)
                elif(invoice != None):
                    dirName = "./assets/results/orders/unknown/" +str(invoice)
                    tag = "invoice"
                    if not os.path.exists(dirName):
                        os.makedirs(dirName)
                    copy(pdf, dirName)
                else:
                    driName = None
                print( "Extracted -- Order : " + str(order) +" -- Invoice : " + str(invoice))
                print("Process 4/4 : Extracting product quantities from the Doc")
                quantity,qty_list = extract_quantity(image,contents,file_name)
                print("Quantities Identified : " + str(qty_list))
                print("Total : " + str(quantity))
                print("Successfully Completed Processing " + file_name + " :)")
            except:
                code = "FAILURE"
                message = "Vision/Extraction Issue"
                return json.dumps({"code": code , "message" : message})
            
            #API to fetch and check whether the documents are already present
            CHECK_API_ENDPOINT = "http://localhost:3000/api/documents/count?where="
            PARAMS = json.dumps({"filename":file_name})
            r = requests.get(url = CHECK_API_ENDPOINT+PARAMS)
            json.loads(r.text)['count']
            if(json.loads(r.text)['count'] == 0):
                data = {
                          "order": str(order),
                          "invoice": str(invoice),
                          "document_tag": str(tag),
                          "path": str(dirName),
                          "filename": str(file_name),
                          "quantity": str(quantity),
                        }

                # sending post request and saving response as response object 
                try:
                    r = requests.post(url = API_ENDPOINT, data = data) 
                except:
                    code = "FAILURE"
                    message = "Database Error"
                    return json.dumps({"code": code , "message" : message})
    code = "SUCCESS"
    message = "Document Classified"
    return json.dumps({"code": code , "message" : message})