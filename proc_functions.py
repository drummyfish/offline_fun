## Definition of proc functions. Helper class FunHTMLParser can
#  be used. To test your proc functions call this file with Python.

import sys
import urllib2
from fun_html_parser import FunHTMLParser

#================================================
#               PROC FUNCTIONS:
#================================================

def wiki(html):                                         ##< for Wikipedia and Wikia pages, leaves only content
  parser = FunHTMLParser()
  html = parser.leave_only_subtrees(html,"","content")
  html = parser.delete_subtrees(html,"","Lists_in_Wikipedia")
  html = novideo(html)
  return html

def nojs(html):                                         ##< removes JavaScript
  parser = FunHTMLParser()
  return parser.delete_subtrees(html,"script")

def noimg(html):
  parser = FunHTMLParser()
  return parser.delete_subtrees(html,"img")

def novideo(html):
  parser = FunHTMLParser()
  return parser.delete_subtrees(html,"video") 

def imperial_lib(html):
  parser = FunHTMLParser()
  return parser.leave_only_subtrees(html,"","main")

def reddit(html):
  parser = FunHTMLParser()
  html = parser.leave_only_subtrees(html,"div","","content")
  html = parser.delete_subtrees(html,"ul","","flat-list buttons")
  return html

def add_css(html, css_filename):
  parser = FunHTMLParser()
  return parser.add_to_head(html,"<link rel=\"stylesheet\" href=\"" + css_filename + "\">")

# Add your own functions here

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
