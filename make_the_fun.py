import re
import urllib
import urllib2
import os.path
import time
import proc_functions
import shutil
import fun_html_parser

CONTENT_FILE = "content_file.txt"
OUTPUT_FOLDER = "output"
OUTPUT_FOLDER_SUBFOLDER = "content"
MAX_ATTEMPTS = 5
ATTEMPT_WAIT = 3
DEFAULT_CSS = "g.css"

COOKIES = (
  ("over18","1"),           # for reddit
  )

EXTENSIONS_WEBPAGE = (".html",".htm")
EXTENSIONS_TEXT = (".txt",)
EXTENSIONS_IMAGE = (".jpg",".jpeg",".bmp",".png",".tiff",".svg",".gif")

EXTENSIONS = EXTENSIONS_WEBPAGE + EXTENSIONS_TEXT + EXTENSIONS_IMAGE

FILETYPE_WEBPAGE = 0
FILETYPE_IMAGE = 1
FILETYPE_TEXT = 2
FILETYPE_PDF = 3
FILETYPE_UNKNOWN = 4

def get_filetype(url):
  extension = get_extension(url)

  if extension in EXTENSIONS_WEBPAGE:
    return FILETYPE_WEBPAGE
  elif extension in EXTENSIONS_IMAGE:
    return FILETYPE_IMAGE
  elif extension in EXTENSIONS_TEXT:
    return FILETYPE_TEXT

  return FILETYPE_UNKNOWN

def make_index_page(processed_downloads):
  result = "<html><head><meta charset=\"UTF-8\"><title>offline fun - index</title>\n"
  result += ("<script>\n"
             "function onload() {\n"
             "var link_element = document.createElement(\"a\");\n"
             "var a_elements = document.getElementsByTagName(\"a\");\n"
             "var random_link = a_elements[Math.floor(Math.random()*a_elements.length)];\n"
             "link_element.innerHTML = \"random page\";\n"
             "link_element.className = \"offline_fun_random\";\n"
             "link_element.setAttribute(\"href\",random_link);\n"
             "document.body.insertBefore(link_element,document.body.childNodes[3]); }\n"
             "</script>\n")

  result += "</head><body onload=\"onload()\">\n"  
  result += "<h1>Offline Fun</h1>\n"

  processed_downloads = sorted(processed_downloads, key=lambda item: item[2])

  previous_cathegory = None

  for page in processed_downloads:
    if page[2] != previous_cathegory:
      if previous_cathegory != None:
        result += "</ul>\n"

      previous_cathegory = page[2]

      result += "<h2>" + page[2] + "</h2>\n"
      result += "<ul>\n"   # start a new list

    result += "<li><a href=\"" + os.path.join(OUTPUT_FOLDER_SUBFOLDER,page[0]) + "\">" + page[1] + "</a></li>"

  result += "</ul>\n"
  result += "</body></html>\n"

  return result

def cookies_string(cookies):
  result = ""
  first = True

  for cookie in cookies:
    if first:
      first = False
    else:
      result += ";"

    result += cookie[0] + "=" + cookie[1]

  return result

def add_page_header(html, original_url, title):
  parser = fun_html_parser.FunHTMLParser()
  html_code = ("<div id=\"offline_fun_header\" style=\"margin: 20px 0; padding: 20px; background-color: "
               "rgb(232,145,84);\"> <a href=\"../index.html\">back</a> to index, offline "
               "fun index - <a href=\"" + original_url + "\">" + title + "</a></div>\n")
  return parser.add_to_body(html,html_code)

def get_extension(url):
  extension = url[url.rfind("."):].lower()

  if not extension in EXTENSIONS:
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
  url = re.sub("^(https?|)://","",url)
  url = re.sub("[\./]","_",url)

  url += extension

  return url

def relative_to_absolute_url(url,complete_url):
  if len(url) == 0 or url[0] != "/":
    return url

  prefix = complete_url[:re.search("(^[^/]*//[^/]+)",complete_url).end(1)]

  return prefix + url

def correct_links(html,url):
  result = ""
  position = 0

  for match in re.finditer(" (href|src) *= *[\"']([^\"']*)[\"']",html):
    result += html[position:match.start(2)]
    result += url_to_filename(relative_to_absolute_url(html[match.start(2):match.end(2)],url))
    position = match.end(2)

  result += html[position:]

  return result

#================================================================
#                            Main
#================================================================

data_folder = os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER)

shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER)
os.makedirs(os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER))

error_count = 0

processed_downloads = []    # list of tuples: (filename, page title, cathegory)

with open(CONTENT_FILE,"r") as content_file:
  for line in content_file:
    line = line[:-1].rstrip().lstrip()        # remove '\n' and l/r whitespaces

    if len(line) == 0 or line[0] == "#":      # comment or empty line
      continue

    splitted = line.split("\t")

    url = splitted[0]

    filetype = get_filetype(url)

    if filetype in (FILETYPE_WEBPAGE,FILETYPE_TEXT):
      #========= WEBPAGE ==========
      proc_function_names = ""
      list_under = "other"                      # default cathegory
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

      print("downloading page: " + url)

      attempt_count = 0

      while attempt_count < MAX_ATTEMPTS:
        try:
          opener = urllib2.build_opener()
          opener.addheaders.append(("Cookie",cookies_string(COOKIES)))
          webpage_data = opener.open(url)
          html = webpage_data.read()
          break
        except Exception:
          print("error downloading the page, trying again...")
          attempt_count += 1

          if attempt_count == MAX_ATTEMPTS:
            print("failed too many times, going on...")
            error_count += 1
          else:
            time.sleep(ATTEMPT_WAIT)

      print("processing")

      page_title = get_html_title(html)

      if page_title == "":
        page_title = url

      html = correct_links(html,url)

      if len(css_name) != 0:        # handle css
        html = proc_functions.add_css(html,css_name)
        shutil.copyfile(css_name,os.path.join(OUTPUT_FOLDER,OUTPUT_FOLDER_SUBFOLDER,css_name))

      try:
        html = proc_functions.apply_proc_functions(html,proc_function_names)
      except AttributeError as e:
        print("error applying proc functions: " + proc_function_names)
        error_count += 1

      html = add_page_header(html,url,page_title)

      processed_downloads.append( (filename,page_title,list_under) )

      text_file = open(os.path.join(data_folder,filename),"w")
      text_file.write(str(html))
      text_file.close()
    elif filetype == FILETYPE_IMAGE:
      #========= IMAGE ==========
      print("downloading image: " + url)

      imagefile = urllib.URLopener()
      filename = url_to_filename(url)
      imagefile.retrieve(url,os.path.join(data_folder,filename))

      processed_downloads.append( (filename,url,"resources") )

print("making the index page")

text_file = open(os.path.join(OUTPUT_FOLDER,"index.html"),"w")
text_file.write(proc_functions.add_css(make_index_page(processed_downloads),os.path.join(OUTPUT_FOLDER_SUBFOLDER,DEFAULT_CSS)))
text_file.close()

print("Completed with " + str(error_count) + " errors.")
