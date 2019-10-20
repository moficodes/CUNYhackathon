import json
import subprocess
import time
from datetime import datetime, timedelta
import gphoto2 as gp
import signal, os, subprocess
import random
from PIL import Image, ImageDraw
from twilio.rest import Client
import ibm_boto3
from ibm_botocore.client import Config, ClientError


COS_ENDPOINT = "https://s3.us-east.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "Xc6U42S2I6wFDZ2sgAXqknqZqk1qAK6GRfWn-yzcszjo"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/b8e8d442933a88b81025d9779bd23971:35f0b32b-b048-4b00-9bb7-84af15f5ce96::"

#create resource
cos = ibm_boto3.resource("s3",
                         ibm_api_key_id =COS_API_KEY_ID,
                         ibm_service_instance_id=COS_RESOURCE_CRN,
                         ibm_auth_endpoint=COS_AUTH_ENDPOINT,
                         config=Config(signature_version="oauth"),
                         endpoint_url=COS_ENDPOINT
)
# 
# #shot_date = datetime.now().strftime("%Y-%m-%d")
# 
# def get_buckets():
#     print("Retrieving list of buckets")
#     try:
#         buckets = cos.buckets.all()
#         for bucket in buckets:
#             print("Bucket Name: {0}".format(bucket.name))
#     except ClientError as be:
#         print("CLIENT ERROR: {0}\n".format(be))
#     except Exception as e:
#         print("Unable to retrieve list buckets: {0}".format(e))
#         
# get_buckets()
# 
def resize(input_file):
    
    image_Path_Input = '/home/pi/Desktop/CUNY/Images/'
    image_Path_Output = '/home/pi/Desktop/CUNY/Output/'

    

    im = Image.open(image_Path_Input + input_file)
    im_width, im_height = im.size

    print('im.size', im.size)
    im = im.resize((int(im_width/4), int(im_height/4)), Image.ANTIALIAS)

   

    im.save(image_Path_Output + input_file)
#

def send_message(message_body):
    account_sid = "AC30668d739d5127e3d11129ae7b73b51e"
    auth_token = "e5967cd1b81237669c0d1df983093267"

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body = message_body,
        from_ = "+12027592241",
        to = "+17174303482"
        )

    print(message.sid)

def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        part_size = 1024 * 1024 * 5
        
        file_threshold = 1024 * 1024 * 15
        
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold = file_threshold,
            multipart_chunksize = part_size
        )
        
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )
            
        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))
#             
# 
#             
# 
# # 
# 
# # 
# # 
# # 
# 
# save_location = "/home/pi/Desktop/CUNY/" 
# # 
# # def createSaveFolder():
# #     try:
# #         os.makedirs(save_location)
# #         os.chdir(save_location)
# #     except:
# #         print("Failed to create the new directory")
# #     os.chdir(save_location)
# #

# def recognize(image_file):
#     with open(image_file) as images_file:
#         classes = visual_recognition.analyze(
#             images_file,
#             threshold='0.6',
#             classifier_ids='forest-state_605719189').get_result()
#     print(json.dumps(classes, indent=2))



def captureImages(end_time):
      
    while datetime.now() < end_time:
        picName = datetime.now().strftime("%H:%M:%S") + str(random.randint(1,999)) + ".jpg" 
        os.system("gphoto2 --capture-image-and-download --filename Images/" + picName)
        resize(picName)
        # visual reco
#         data = recognize("Output/"+picName)
        # determine if we should send message
        #
        
        returned_output = subprocess.check_output(['curl', '-s', '-X', 'POST', '-u', "apikey:uroeHuBUwUoYBOhtAyO6HoFjXqC_WQpxaIndZowZgTGk", '-F', "images_file=@Output/"+picName, '-F', "threshold=0.6", '-F', "classifier_ids=forest-state_605719189", "https://gateway.watsonplatform.net/visual-recognition/api/v3/classify?version=2018-03-19"])

        classify = json.loads(returned_output)["images"][0]["classifiers"][0]["classes"][0]["class"]
        # send message
        if classify == "fire":
            #send message with body fire
            send_message("There is a fire 🔥🔥🔥")
            print("fire")
        elif classify == "deforest":
            #send message with body deforest
            send_message("The forest is gone 😢😢😢")
            print("deforest")
        
        # add text to image
        img = Image.open("Output/"+picName)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("CaviarDreams.ttf", 48)
        draw.text((0, 0),classify,(255,255,255),font=font)
        img.save("Output/"+picName)

        
        
        multi_part_upload('hackathon2019', picName, '/home/pi/Desktop/CUNY/Images/'+picName)
        time.sleep(2)
        os.system("rm Images/*")
        os.system("rm Output/*")
        time.sleep(1)
#         
# # 
# #         
# #         
# #         
# # # def framesToVideo(input_List, output_File_Name, fourcc, fps, size):
# # #     #output video writer object
# # #     out = cv2.VideoWriter(output_File_Name, fourcc, fps, size)
# # #     
# # #     num_Frames = len(input_List)
# # #     
# # #     for i in range(num_Frames):
# # #         base_name = 
# #     
# #     
# #     
# #     
# # createSaveFolder()
# captureImages(datetime.now() + timedelta(seconds = 120))
# 
# # for name in picsArray:
# #     
# #     print(name)
# 
# 
# 
# 
# 
#
# def get_bucket_contents(bucket_name):
#     print("Retrieving bucket contents from: {0}".format(bucket_name))
#     try:
#         files = cos.Bucket(bucket_name).objects.all()
#         for file in files:
#             print("Item: {0} ({1} bytes).".format(file.key, file.size))
#     except ClientError as be:
#         print("CLIENT ERROR: {0}\n".format(be))
#     except Exception as e:
#         print("Unable to retrieve bucket contents: {0}".format(e))
#         
# get_bucket_contents('hackathon2019')
