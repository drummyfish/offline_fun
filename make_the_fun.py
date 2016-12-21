import re
import urllib2
import os.path
import time
import proc_functions
import shutil

CONTENT_FILE = "content_file.txt"
OUTPUT_FOLDER = "output"
OUTPUT_FOLDER_SUBFOLDER = "content"

def get_extension(url):
  extension = url[url.rfind("."):]

  if extension != ".html" and extension != ".txt":
    extension = ".html"

  return extension

def url_to_filename(url):
  extension = get_extension(url)
  
  url = re.sub("\n","",url)
  url = re.sub("^https?://","",url)
  url = re.sub("[\./]","_",url)

  url += extension

  print(url)
  return url

data_folder = os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER)

shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER)
os.makedirs(os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER))

with open(CONTENT_FILE,"r") as content_file:
  for line in content_file:
    line = line[:-1]              # remove '\n'

    splitted = line.split("\t")

    url = splitted[0]

    proc_function_names = ""
    list_under = ""
    css_name = ""

    for attribute in splitted[1:]:
      attribute_splitted = attribute.split(":")

      if len(attribute_splitted) != 2:
        continue

      attr_name = attribute_splitted[0]
      attr_value = attribute_splitted[1]

      if attr_name == "proc":
        proc_function_names = attr_value
      elif attr_name == "under":
        list_under = attr_value
      elif attr_name == "css":
         css_name = attr_value

    filename = url_to_filename(url)

    print("downloading: " + url)
    webpage_data = urllib2.urlopen(url)
    html = webpage_data.read()

    if len(css_name) != 0:        # handle css
      html = proc_functions.add_css(html,css_name)
      shutil.copyfile(css_name,os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER,css_name))

    html = proc_functions.apply_proc_functions(html,proc_function_names)

    text_file = open(os.path.join(data_folder,filename),"w")
    text_file.write(str(html))
    text_file.close()
