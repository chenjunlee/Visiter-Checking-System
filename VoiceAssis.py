import glob
import os
import boto3
s3=boto3.client('s3')
i=1
while (i>0):
  filelist=glob.glob("*.jpg")
  for file in filelist:
     name=os.path.basename(file)
	 s3.upload_file(file, 'yourtargetcamera', name, ExtraArgs={'ContentType': "image/jpeg"})
	 os.remove(file)
	 
