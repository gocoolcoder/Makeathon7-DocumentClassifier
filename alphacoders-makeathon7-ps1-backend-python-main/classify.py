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
    if 'textAnnotations' not in json.loads(response.text)['responses'][0].keys():
        return None
    return json.loads(response.text)['responses'][0]['textAnnotations']

#functionality to extract data from each partitions using vision and logics
def extract(ocr_bits,keywords,length,isalphanum):
    value = {}
    for bits in [i.replace("\n"," ").lower().strip() for i in ocr_bits]:
        info = [[],[]]
        for k,v in keywords.items():
            final = list(set(v).intersection(set([item.strip() for item in (bits.replace(" ","\n").replace("\n"," \n").split('\n'))])))
            valid_list = [value for value in bits.split(" ") if value.strip().isdigit() and len(value.strip())>=length]
            if(len(final)>0):
                info[0].append(k)
                info[1].append(bits.index(final[0]))
        if(len(value)<len(keywords)):                  
            if(len(info[0])>1 and len(valid_list)>1):
                ls = [i[1] for i in sorted(zip(info[1],info[0]))]        
                for i in range(len(ls)):
                    value[ls[i]]=valid_list[i]
            elif(len(info[0])==1 and len(valid_list)==1):
                value[info[0][0]] = valid_list[0]
    return value

#functionality to extract quantities present in each document
def extract_quantity(image,contents,file_name):
    for i in range(1,len(contents)):
        data = contents[i]["description"]
        if "qty" in data.lower() or "quantity" in data.lower():
            if("qty" in data.lower()):
                factor = 1.5
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
            cv2.imwrite('./tmp/quantity/'+file_name+'_qty.jpg',image[x1:x2,y1:y2])
            img_for_box_extraction_path = './tmp/quantity/'+file_name+'_qty.jpg'
            height = abs(vert[0]['y']-vert[2]['y'])
            img = cv2.imread(img_for_box_extraction_path, 0)
            thresh2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                      cv2.THRESH_BINARY, 199, 10)
            img_bin = 255 - thresh2
            warn = np.array(img).shape[0]//100
            kernel_length = np.array(img).shape[1]//10
            verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
            hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
            verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
            img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
            horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
            contours, hierarchy = cv2.findContours(horizontal_lines_img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            ls = []
            for i in contours:
                    ls.append(i[0][0][1]) 

            a = sorted(ls)

            b = list(np.diff(a))
            for i in b:
                if i > height*2:
                    idx = b.index(i) 
                    break

            x_a = a[idx]
            x_b = a[idx+1]

            if x_a > height*4:
                x_a = 0 
                x_b = a[idx]

            img = thresh2[x_a:x_b,0:np.array(thresh2).shape[1]]
            scale_percent = 300 
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            cv2.imwrite('./tmp/quantity/'+file_name+'_tmp_qty.jpg',img)
            
            
            
    raw = vision('./tmp/quantity/'+file_name+'_tmp_qty.jpg','TEXT_DETECTION')
    if raw != None:
        raw = raw[0]['description']
        valid_list = [item for item in (raw.replace(".","").replace(",","").split('\n')) if item.strip().isdigit()]
    else:
        valid_list = []
    quantity = 0 
    for qty in valid_list:
        quantity+=int(qty)
    return quantity,valid_list

def tagger(value):
    count = 0
    for k,v in value.items():
        if v != None:
            count = count + 1
            tag = k
    if(count>1):
        tag = "invoice"
    return tag

def create_folder(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    else:
        rmtree(dir_name)
        os.makedirs(dir_name)
    return True

def folder(jobid,tag,value,pdf):
    dir_name = "./assets/results/" + str(jobid) + "/" + str(tag) + "/" + str(value[tag])
    if create_folder(dir_name):
        copy(pdf,dir_name)
        return dir_name

def split(file_name,extension,dir_name,pdf):
    if create_folder(dir_name):
        if(extension.lower()=="pdf"):
            pages = convert_from_path(pdf, 200)
            for index in range(len(pages)):
                pages[0].save(dir_name+'/pdf_img_'+file_name+'.jpg', 'JPEG')
        elif(extension.lower()=="jpg" or extension.lower()=="jpeg" or extension.lower()=="png"):
            im = Image.open('pdf')
            im.save(dir_name+'/pdf_img_'+file_name+'.jpg')
    return True

def create_bits(contents,image,dir_name,keywords):
    for i in range(1,len(contents)):
        data = contents[i]["description"]
        for k,v in keywords.items():
            for value in v:
                if value.lower() in data.lower():
                    vert = contents[i]["boundingPoly"]["vertices"]
                    y1,y2,x1,x2 = min(vert[0]['x'],vert[2]['x']),max(vert[0]['x'],vert[2]['x']),min(vert[0]['y'],vert[2]['y']),max(vert[0]['y'],vert[2]['y'])
                    width = y2-y1
                    height = x2-x1
        #             x1 = max(x1-height*2,0)
                    x_1 = x1
                    x_2 = min(x2+height*4,image.shape[0])
                    y_1 = max(y1-width*2,0)
                    y_2 = min(y2+width*2,image.shape[1])
                    cv2.imwrite(dir_name+'/part'+str(i)+'_1'+'.jpg',image[x_1:x_2,y_1:y_2])
                    y2 = min(y2+width*4,image.shape[1])
                    cv2.imwrite(dir_name+'/part'+str(i)+'_2'+'.jpg',image[x1:x2,y1:y2])
    return True

def job_details(job_id):
    CHECK_API_ENDPOINT = "http://localhost:3000/api/jobs/findone?filter="
    PARAMS = json.dumps({"where":{"jobid":job_id}})
    r = requests.get(url = CHECK_API_ENDPOINT+PARAMS)
    data = json.loads(r.text)
    keywords = data['keywords']
    length = data['length']
    isalphanum = data['isalphanum']
    return keywords, length,  isalphanum

#Main function to classify all the documents


def classify(files,keywords,length,isalphanum):
    counter = 0
    for pdf in files:
        file_name = pdf.split("/")[-1].split(".")[0]
        extension = pdf.split("/")[-1].split(".")[1]
        master_dir_temp = "./tmp/" + file_name + "/"
        dir_name = master_dir_temp + "splits"
        try:
            if(split(file_name,extension,dir_name,pdf)):
                for file in glob.glob(dir_name+'/*.jpg'):
                    dir_name = master_dir_temp + "ocr_bits"
                    if create_folder(dir_name):
                        contents = vision(file,'TEXT_DETECTION')
                        image = cv2.imread(file)
                        if create_bits(contents,image,dir_name,keywords):
                            ocr_bits = []
                            for file in glob.glob(dir_name + './*.jpg'):
                                content = vision(file,'TEXT_DETECTION')
                                ocr_bits.append(content[0]['description'])
                            value = extract(ocr_bits,keywords,length,isalphanum)
                            response = {}
                            for k,v in keywords.items():
                                if k in value.keys():
                                    response[k] = value[k]
                                else:
                                    response[k] = None
                            tag = tagger(value)
                        quantity,qty_list = extract_quantity(image,contents,file_name)

                        order = response['order']
                        invoince = response['invoice']
                        
                        #API to fetch and check whether the documents are already present
                        CHECK_API_ENDPOINT = "http://localhost:3000/api/documents/count?where="
                        PARAMS = json.dumps({"filename":file_name})
                        r = requests.get(url = CHECK_API_ENDPOINT+PARAMS)
                        if(json.loads(r.text)['count'] == 0):
                            data = {
                                      "order": str(response["order"]),
                                      "invoice": str(response["invoice"]),
                                      "document_tag": str(tag),
                                      "path": str(pdf),
                                      "filename": str(file_name),
                                      "quantity": str(quantity)
                                    }

                            # sending post request and saving response as response object 
                            try:
                                r = requests.post(url = API_ENDPOINT, data = data) 
                            except:
                                code = "FAILURE"
                                message = "Database Error"
                                return json.dumps({"code": code , "message" : message})
        except:
            code = "FAILURE"
            message = "Vision/Extraction Issue"
            return json.dumps({"code": code , "message" : message})
                    
        
    code = "SUCCESS"
    message = "Document Classified"
    return json.dumps({"code": code , "message" : message})