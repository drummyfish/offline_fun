import re
import urllib2
import os.path
import time
import proc_functions
import shutil

CONTENT_FILE = "content_file.txt"
OUTPUT_FOLDER = "output"
OUTPUT_FOLDER_SUBFOLDER = "content"
MAX_ATTEMPTS = 3
ATTEMPT_WAIT = 3

def make_index_page(processed_pages):
  result = "<html><head><meta charset=\"UTF-8\"><title>offline fun - index</title></head><body>\n"
  result += "<ul>\n"

  for page in processed_pages:
    result += "<li><a href=\"" + os.path.join(OUTPUT_FOLDER_SUBFOLDER,page[0]) + "\">" + page[1] + "</a></li>"

  result += "</ul>\n"
  result += "</body></html>\n"

  return result

def get_extension(url):
  extension = url[url.rfind("."):]

  if extension != ".html" and extension != ".txt":
    extension = ".html"

  return extension

def get_html_title(html):
  match = re.search("< *title *>([^<]*)</",html)

  if match == None:
    return ""

  return html[match.start(1):match.end(1)]

def url_to_filename(url):
  extension = get_extension(url)
  
  url = re.sub("\n","",url)
  url = re.sub("^https?://","",url)
  url = re.sub("[\./]","_",url)

  url += extension

  return url

data_folder = os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER)

shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER)
os.makedirs(os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER))

error_count = 0

processed_pages = []    # list of tuples: (filename, page title, cathegory)

with open(CONTENT_FILE,"r") as content_file:
  for line in content_file:
    line = line[:-1].rstrip().lstrip()        # remove '\n' and l/r whitespaces

    if len(line) == 0 or line[0] == "#":      # comment or empty line
      continue

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

    attempt_count = 0

    while attempt_count < MAX_ATTEMPTS:
      try:
        webpage_data = urllib2.urlopen(url)
        html = webpage_data.read()
        break
      except Exception:
        print("error downloading the page, trying again...")
        attempt_count += 1

        if attempt_count == MAX_ATTEMPTS:
          print("failed too many times, going on...")
        else:
          time.sleep(ATTEMPT_WAIT)

    print("processing")

    page_title = get_html_title(html)

    if page_title == "":
      page_title = url

    if len(css_name) != 0:        # handle css
      html = proc_functions.add_css(html,css_name)
      shutil.copyfile(css_name,os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER,css_name))

    try:
      html = proc_functions.apply_proc_functions(html,proc_function_names)
    except AttributeError as e:
      print("error applying proc functions: " + proc_function_names)
      error_count += 1

    processed_pages.append( (filename,page_title,list_under) )

    text_file = open(os.path.join(data_folder,filename),"w")
    text_file.write(str(html))
    text_file.close()

print("making the index page")

text_file = open(os.path.join(OUTPUT_FOLDER,"index.html"),"w")
text_file.write(make_index_page(processed_pages))
text_file.close()

print("Completed with " + str(error_count) + " errors.")
