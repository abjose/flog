import Orgnode, datetime, markdown

"""
TODO:
- get jinja2 working
- implement maketree (probably)
- get demo of html working
  title bar with navigation links (nonfunctional)
  tags and filters
- could include basic search: http://lunrjs.com/
- nice simple layout:
  http://hermetic.com/bey/caravan.html
  http://learnlayout.com/display.html

NOTES:
- what if tagged both public and hidden?
- what if link to a non-public thing?
- how to do links?
"""

today = datetime.date.today()
print "Daily plan for", today
print "-------------------------\n"

filename = "demo.org"
nodelist = Orgnode.makelist(filename)

for n in nodelist:
    #if n.Scheduled() == today:
    print "[ ] %s (%s)" % (n.Heading(), n.Tags())
    print n.level
    print n.properties
    print n.Body()
