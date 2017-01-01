from HTMLParser import HTMLParser
import sys
import types
import PIL

def proc_text(input_func):  ##< decorator used for functions that process text (mostly HTML)
  def wrapper(input_text):
    if not type(input_text) is str:
      print("Warning: Can only apply proc func \"" + input_func.__name__ + "\" to string.")
      return input_text

    return input_func(input_text)

  return wrapper

def proc_image(input_func): ##< decorator used for functions that process images
  def wrapper(input_image):

    if not isinstance(input_image,PIL.Image.Image):
      print("Warning: Can only apply proc func \"" + input_func.__name__ + "\" to image.")
      return input_image

    return input_func(input_image)

  return wrapper

## Helper HTML parser class to be used in proc functions.

class FunHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    reload(sys)
    sys.setdefaultencoding('utf-8')

  def attr_has_value(self, attrs, attr_name, value):
    for attr in attrs:
      if attr[0] == attr_name and attr[1] == value:
        return True

    return False

  def tag_html(self, tag, attrs):
    result = "<" + tag

    for attr in attrs:
      result += " " + str(attr[0]) + "=\"" + str(attr[1]) + "\""

    return result + ">"

  def endtag_html(self, tag):
    return "</" + tag + ">"

  def __add_after_tag(self, html, text, tag):                 ##< Helper method, adds given text after 1st found specified tag
    def starttag_func(self, tag, attrs):
      self.result += self.tag_html(tag,attrs)

      if tag == self.looking_for_tag:
        self.result += self.text_to_insert

    def endtag_func(self, tag):
      self.result += self.endtag_html(tag)

    def data_func(self, data):
      self.result += data

    self.handle_starttag = types.MethodType(starttag_func,self)
    self.handle_endtag = types.MethodType(endtag_func,self)
    self.handle_data = types.MethodType(data_func,self)

    self.looking_for_tag = tag
    self.text_to_insert = text
    self.result = ""
    self.feed(html)

    return self.result    

  def add_to_head(self, html, text):                          ##< Adds specified text to the head of HTML. 
    return self.__add_after_tag(html,text,"head")

  def add_to_body(self, html, text):                          ##< Adds specified text to the body of HTML. 
    return self.__add_after_tag(html,text,"body")

  def compress(self, html):                                   ##< Doesn't change the HTML semantics, only compresses it to more compact form.
    def starttag_func(self, tag, attrs):
      self.result += self.tag_html(tag,attrs)

    def endtag_func(self, tag):
      self.result += self.endtag_html(tag)

    def data_func(self, data):
      self.result += data

    self.handle_starttag = types.MethodType(starttag_func,self)
    self.handle_endtag = types.MethodType(endtag_func,self)
    self.handle_data = types.MethodType(data_func,self)

    self.result = ""
    self.feed(html)

    return self.result

  def html_prolog(self, html):                                ##< Gets the strat of given HTML up untill body (including)
    def starttag_func(self, tag, attrs):
      if self.done:
        return

      self.result += self.tag_html(tag,attrs)

      if tag == "body":
        self.done = True

    def endtag_func(self, tag):
      if self.done:
        return

      self.result += self.endtag_html(tag)

    def data_func(self, data):
      if self.done:
        return

      self.result += data

    self.handle_starttag = types.MethodType(starttag_func,self)
    self.handle_endtag = types.MethodType(endtag_func,self)
    self.handle_data = types.MethodType(data_func,self)

    self.done = False
    self.result = ""
    self.feed(html)

    return self.result    

  def html_epilog(self):                                      ##< Gets the end of HTML document
    return "</body></html>"

  def delete_subtrees(self, html, tag_name, tag_id="", tag_class=""):     ##< Deletes all subtrees meeting a condition.
    return self.__filter(html, tag_name, tag_id, tag_class, False)        #   Tag, name or class can be empty ("") to be ignored.
    
  def leave_only_subtrees(self, html, tag_name, tag_id="", tag_class=""): ##< Leaves only subtrees meeting given condition (html, body and head stays).
                                                                          #   Tag, name or class can be empty ("") to be ignored.
    return self.html_prolog(html) + self.__filter(html, tag_name, tag_id, tag_class, True) + self.html_epilog()

  def __filter(self, html, tag_name, tag_id, tag_class, include=True):    ##< Helper method, either leaves only given subtrees (include == True)
                                                                          #   or deletes all such subtrees (include == False)
    def starttag_func(self, tag, attrs):
      inside = False

      if ( (len(self.tag_name) == 0 or self.tag_name == tag) and
           (len(self.tag_id) == 0 or self.attr_has_value(attrs,"id",self.tag_id)) and
           (len(self.tag_class) == 0 or self.attr_has_value(attrs,"class",self.tag_class)) ):
        self.looking_for_tag = tag
        self.depth = 0
        self.id_found = True
      
      if self.id_found:
        if tag == self.looking_for_tag:
          self.depth += 1

        inside = True

      if self.include == inside:
        self.result += self.tag_html(tag,attrs)

    def endtag_func(self, tag):
      inside = False

      if self.id_found:
        inside = True

        if tag == self.looking_for_tag:
          self.depth -= 1

          if self.depth == 0:
            self.id_found = False

      if self.include == inside:
        self.result += self.endtag_html(tag)

    def data_func(self, data):
      inside = self.id_found

      if self.include == inside:
        self.result += data

    self.handle_starttag = types.MethodType(starttag_func,self)
    self.handle_endtag = types.MethodType(endtag_func,self)
    self.handle_data = types.MethodType(data_func,self)

    self.id_found = False
    self.include = include
    self.tag_id = tag_id
    self.tag_name = tag_name
    self.tag_class = tag_class
    self.looking_for_tag = ""
    self.depth = 0
    self.result = ""
    self.feed(html)

    return self.result
    
