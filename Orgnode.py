# Copyright (c) 2010 Charles Cave
#
#  Permission  is  hereby  granted,  free  of charge,  to  any  person
#  obtaining  a copy  of  this software  and associated  documentation
#  files   (the  "Software"),   to  deal   in  the   Software  without
#  restriction, including without limitation  the rights to use, copy,
#  modify, merge, publish,  distribute, sublicense, and/or sell copies
#  of  the Software, and  to permit  persons to  whom the  Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# Program written by Charles Cave   (charlesweb@optusnet.com.au)
# February - March 2009
# Version 2 - June 2009
#   Added support for all tags, TODO priority and checking existence of a tag
# More information at
#    http://members.optusnet.com.au/~charles57/GTD

"""
The Orgnode module consists of the Orgnode class for representing a
headline and associated text from an org-mode file, and routines for
constructing data structures of these classes.
"""

import re, sys
import datetime

def makelist(filename):
   """
   Read an org-mode file and return a list of Orgnode objects
   created from this file.
   """
   try:
      f = open(filename, 'r')
   except IOError:
      print("Unable to open file [%s] " % filename)
      print("Program terminating.")
      sys.exit(1)

   todos         = dict()  # populated from #+SEQ_TODO line
   todos['TODO'] = ''   # default values
   todos['DONE'] = ''   # default values
   level         = 0
   heading       = ""
   bodytext      = ""
   tag1          = ""      # The first tag enclosed in ::
   alltags       = []      # list of all tags in headline
   sched_date    = ''
   deadline_date = ''
   nodelist      = []
   propdict      = dict()

   for line in f:
      hdng = re.search('^(\*+)\s(.*?)\s*$', line)
      if hdng:
         if heading:  # we are processing a heading line
            thisNode = Orgnode(level, heading, bodytext, tag1, alltags)
            if sched_date:
               thisNode.setScheduled(sched_date)
               sched_date = ""
            if deadline_date:
               thisNode.setDeadline(deadline_date)
               deadline_date = ''
            thisNode.setProperties(propdict)
            nodelist.append( thisNode )
            propdict = dict()
         level = hdng.group(1)
         heading =  hdng.group(2)
         bodytext = ""
         tag1 = ""
         alltags = []       # list of all tags in headline
         tagsrch = re.search('(.*?)\s*:(.*?):(.*?)$',heading)
         if tagsrch:
            heading = tagsrch.group(1)
            tag1 = tagsrch.group(2)
            alltags.append(tag1)
            tag2 = tagsrch.group(3)
            if tag2:
               for t in tag2.split(':'):
                  if t != '': alltags.append(t)
      else:      # we are processing a non-heading line
         if line[:10] == '#+SEQ_TODO':
            kwlist = re.findall('([A-Z]+)\(', line)
            for kw in kwlist: todos[kw] = ""

         if re.search(':PROPERTIES:', line): continue
         if re.search(':END:', line): continue
         prop_srch = re.search('^\s*:(.*?):\s*(.*?)\s*$', line)
         if prop_srch:
            propdict[prop_srch.group(1)] = prop_srch.group(2)
            continue
         sd_re = re.search('SCHEDULED:\s+<([0-9]+)\-([0-9]+)\-([0-9]+)', line)
         if sd_re:
            sched_date = datetime.date(int(sd_re.group(1)),
                                       int(sd_re.group(2)),
                                       int(sd_re.group(3)) )
         dd_re = re.search('DEADLINE:\s*<(\d+)\-(\d+)\-(\d+)', line)
         if dd_re:
            deadline_date = datetime.date(int(dd_re.group(1)),
                                          int(dd_re.group(2)),
                                          int(dd_re.group(3)) )

         # if line[:1] != '#':
         bodytext = bodytext + line

   # write out last node
   thisNode = Orgnode(level, heading, bodytext, tag1, alltags)
   thisNode.setProperties(propdict)
   if sched_date:
      thisNode.setScheduled(sched_date)
   if deadline_date:
      thisNode.setDeadline(deadline_date)
   nodelist.append( thisNode )

   # using the list of TODO keywords found in the file
   # process the headings searching for TODO keywords
   for n in nodelist:
      h = n.Heading()
      todoSrch = re.search('([A-Z]+)\s(.*?)$', h)
      if todoSrch:
         if todos.has_key( todoSrch.group(1) ):
            n.setHeading( todoSrch.group(2) )
            n.setTodo ( todoSrch.group(1) )
      prtysrch = re.search('^\[\#(A|B|C)\] (.*?)$', n.Heading())
      if prtysrch:
         n.setPriority(prtysrch.group(1))
         n.setHeading(prtysrch.group(2))

   return nodelist

def maketree(title, filename):
   """
   Read an org-mode file and return a tree of Orgnode objects
   created from this file.
   """
   # get "bare" text (i.e. text for root node)
   try:
      f = open(filename, 'r')
   except IOError:
      print("Unable to open file [%s] " % filename)
      print("Program terminating.")
      sys.exit(1)

   root_text = ""
   for line in f:
      if "*" in line: break
      root_text += line

   root = Orgnode([], title, root_text, "", [])

   # iterate over parsed node, generating tree as you go
   node_list = makelist(filename)
   parents = []
   curr_level = 0
   prev_node = root
   for node in node_list:
      if   node.level > curr_level: parents.append(prev_node)
      elif node.level < curr_level: parents = parents[:node.level]
      curr_level = node.level
      # append node to current parent
      parents[-1].addChild(node)
      node.setParent(parents[-1])
      prev_node = node

   return root

######################
class Orgnode(object):
   """
   Orgnode class represents a headline, tags and text associated
   with the headline.
   """
   def __init__(self, level, headline, body, tag, alltags):
      """
      Create an Orgnode object given the parameters of level (as the
      raw asterisks), headline text (including the TODO tag), and
      first tag. The makelist routine postprocesses the list to
      identify TODO tags and updates headline and todo fields.
      """
      self.level = len(level)
      self.headline = headline
      self.body = body
      self.tag = tag            # The first tag in the list
      self.tags = dict()        # All tags in the headline
      self.todo = ""
      self.prty = ""            # empty of A, B or C
      self.scheduled = ""       # Scheduled date
      self.deadline = ""        # Deadline date
      self.properties = dict()
      for t in alltags:
         self.tags[t] = ''

      self.parent = None
      self.children = []

      # Look for priority in headline and transfer to prty field

   def Heading(self):
      """
      Return the Heading text of the node without the TODO tag
      """
      return self.headline

   def setHeading(self, newhdng):
      """
      Change the heading to the supplied string
      """
      self.headline = newhdng

   def Body(self):
      """
      Returns all lines of text of the body of this node except the
      Property Drawer
      """
      return self.body

   def Content(self):
      """
      Returns all lines of text (including title) of this node, not including
      properties and tags
      """
      return self.headline + '\n' + self.body

   def LeafContent(self):
      """
      Get all content as if this were a 'leaf' node (i.e. want to treat children
      only as text, not as proper pages in themselves).
      """
      return self.Body() + "\n".join([c.Content() for c in self.children])

   def Level(self):
      """
      Returns an integer corresponding to the level of the node.
      Top level (one asterisk) has a level of 1.
      """
      return self.level

   def Breadcrumbs(self):
      """
      Return a list of (URL, headline) tuples, from root to this node, to
      facilitate constructing a 'breadcrumb' link sequence.
      """
      # TODO: handle cycles...
      crumbs = [] if self.parent is None else self.parent.Breadcrumbs()
      return crumbs + [(self.URL(), self.Heading())]

   def Priority(self):
      """
      Returns the priority of this headline: 'A', 'B', 'C' or empty
      string if priority has not been set.
      """
      return self.prty

   def setPriority(self, newprty):
      """
      Change the value of the priority of this headline.
      Values values are '', 'A', 'B', 'C'
      """
      self.prty = newprty

   def Tag(self):
      """
      Returns the value of the first tag.
      For example, :HOME:COMPUTER: would return HOME
      """
      return self.tag

   def Tags(self):
      """
      Returns a list of all tags
      For example, :HOME:COMPUTER: would return ['HOME', 'COMPUTER']
      """
      return self.tags.keys()

   def hasTag(self, srch):
      """
      Returns True if the supplied tag is present in this headline
      For example, hasTag('COMPUTER') on headling containing
      :HOME:COMPUTER: would return True.
      """
      #return self.tags.has_key(srch)
      return srch in self.tags

   def setTag(self, newtag):
      """
      Change the value of the first tag to the supplied string
      """
      self.tag = newtag

   def setTags(self, taglist):
      """
      Store all the tags found in the headline. The first tag will
      also be stored as if the setTag method was called.
      """
      for t in taglist:
         self.tags[t] = ''

   def HTMLFriendlyTags(self):
      """
      Only return tags you want to show up on the site.
      """
      ignore_list = ["leaf", "private"]
      return [k for k in self.tags.keys() if k not in ignore_list]

   def Todo(self):
      """
      Return the value of the TODO tag
      """
      return self.todo

   def setTodo(self, value):
      """
      Set the value of the TODO tag to the supplied string
      """
      self.todo = value

   def setProperties(self, dictval):
      """
      Sets all properties using the supplied dictionary of
      name/value pairs
      """
      self.properties = dictval

   def Property(self, keyval):
      """
      Returns the value of the requested property or null if the
      property does not exist.
      """
      return self.properties.get(keyval, "")

   def HTMLFriendlyProperties(self):
      """
      Return a list of property:value pairs, made HTML-friendly if necessary.
      """
      items = []
      ignore = ['description', 'picture']
      date_like = ["date", "started", "updated"]
      for k,v in self.properties.items():
         if k in ignore: continue
         # address any special cases
         if k in date_like: v = v[1:-1].split(' ')[0]
         items.append((k, v))
      return items

   def projectDate(self):
      """
      Return a representative date for this node, if possible.
      - if "updated" property is defined, return that
      - otherwise, if "started" or "date" property is defined, return that
      """
      html_props = dict(self.HTMLFriendlyProperties())
      date_priority = ["updated", "started", "date"]
      for key in date_priority:
         if key in html_props:
            return html_props[key]
      return ""

   def setScheduled(self, dateval):
      """
      Set the scheduled date using the supplied date object
      """
      self.scheduled = dateval

   def Scheduled(self):
      """
      Return the scheduled date object or null if nonexistent
      """
      return self.scheduled

   def setDeadline(self, dateval):
      """
      Set the deadline (due) date using the supplied date object
      """
      self.deadline = dateval

   def Deadline(self):
      """
      Return the deadline date object or null if nonexistent
      """
      return self.deadline

   def setParent(self, parent):
      """
      Update parent of this node.
      """
      self.parent = parent

   def addChild(self, child):
      """
      Add a child to the children list.
      """
      self.children.append(child)

   def URL(self):
      """
      Return the 'URL' of the headline (spaces replaced with dashes).
      """
      # TODO: confusing to handle "index" case in here.
      if self.parent is None:
         return "index.html"

      remove = ['.', ',', '?', '=', '&']
      url = self.headline.lower()
      for c in remove: url = url.replace(c, '')
      return url.replace(' ', '-') + ".html"

   def __repr__(self):
      """
      Print the level, heading text and tag of a node and the body
      text as used to construct the node.
      """
      # This method is not completed yet.
      n = ''
      for i in range(0, self.level):
         n = n + '*'
      n = n + ' ' + self.todo + ' '
      if self.prty:
         n = n +  '[#' + self.prty + '] '
      n = n + self.headline
      n = "%-60s " % n     # hack - tags will start in column 62
      closecolon = ''
      for t in self.tags.keys():
         n = n + ':' + t
         closecolon = ':'
      n = n + closecolon
      # Need to output Scheduled Date, Deadline Date, property tags The
      # following will output the text used to construct the object
      n = n + "\n" + self.body

      return n
