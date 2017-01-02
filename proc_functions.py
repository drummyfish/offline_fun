## Definition of proc functions. Helper class FunHTMLParser and decorators can
#  be used. To test your proc functions call this file with Python.

import sys
import urllib2
from fun_html_parser import FunHTMLParser, proc_text, proc_image
from PIL import Image

#================================================
#               PROC FUNCTIONS:
#================================================

@proc_text
def wiki(html):                                         ##< for Wikipedia and Wikia pages, leaves only content
  parser = FunHTMLParser()
  html = parser.leave_only_subtrees(html,"","content")
  html = parser.delete_subtrees(html,"","Lists_in_Wikipedia")
  html = novideo(html)
  return html

@proc_text
def nojs(html):                                         ##< removes JavaScript
  parser = FunHTMLParser()
  return parser.delete_subtrees(html,"script")

@proc_text
def noimg(html):                                        ##< removes images
  parser = FunHTMLParser()
  return parser.delete_subtrees(html,"img")

@proc_text
def novideo(html):                                      ##< removes videos
  parser = FunHTMLParser()
  return parser.delete_subtrees(html,"video") 

@proc_text
def imperial_lib(html):                                 ##< for imperial library website
  parser = FunHTMLParser()
  return parser.leave_only_subtrees(html,"","main")

@proc_text
def reddit(html):                                       ##< for reddit
  parser = FunHTMLParser()
  html = parser.leave_only_subtrees(html,"div","","content")
  html = parser.delete_subtrees(html,"ul","","flat-list buttons")
  return html

@proc_text
def onlypre(html):
  parser = FunHTMLParser()
  html = parser.leave_only_subtrees(html,"pre","","")
  return html

@proc_image
def small(img):                                         ##< resizes the image to small
  return img.resize((200,200))

@proc_image
def medium(img):                                        ##< resizes the image to small
  return img.resize((512,512))

# Add your own functions here

#================================================
# Following functions are NOT to be used from the
# content_file.txt.

def add_css(html, css_filename):
  parser = FunHTMLParser()
  return parser.add_to_head(html,"<link rel=\"stylesheet\" href=\"" + css_filename + "\">")

#================================================

def apply_proc_functions(html, proc_function_names):      ##< Applies the proc functions whose names are given in string (separated with commas)
  function_list = proc_function_names.split(",")

  for function_name in function_list:
    if len(function_name) == 0:
      continue

    proc_func = getattr(sys.modules[__name__],function_name)

    if proc_func != None:
      html = proc_func(html)
  
  return html

def apply_proc_functions_image(image_path, proc_function_names):
  if len(proc_function_names) == 0:
    return

  function_list = proc_function_names.split(",")

  image = Image.open(image_path)

  for function_name in function_list:
    if len(function_name) == 0:
      continue

    proc_func = getattr(sys.modules[__name__],function_name)

    if proc_func != None:
      image = proc_func(image)

  image.save(image_path)

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("you can test the proc function by calling this script with 2 arguments:")
    print("  - website url")
    print("  - proc function name")
  else:
    webpage_data = urllib2.urlopen(sys.argv[1])
    html = webpage_data.read()

    text_file = open("test_output.html","w")

    new_html = apply_proc_functions(html,sys.argv[2])

    text_file.write(new_html)
    text_file.close()
