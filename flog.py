import Orgnode, datetime, markdown, sys
from jinja2 import Environment, FileSystemLoader

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

def make_site(root, project_template, page_template):
    write_page(root.URL(), get_page(root, project_template, page_template))
    if not root.hasTag('leaf'):
        for child in root.children:
            make_site(child, project_template, page_template)

def write_page(name, content):
    filename = 'output/' + name + '.html'
    with open(filename, 'w') as f:
        f.write(content)

def get_page(node, project_template, page_template):
    projects = get_projects(node, project_template)
    content = get_content(node)
    #print content
    return page_template.render(projects=projects, content=content)

def get_content(node):
    content = node.LeafContent() if node.hasTag('leaf') else node.Body()
    content = content.strip()
    print content
    return markdown.markdown(content)

def get_projects(node, project_template):
    return [project_template.render(node=child) for child in node.children]

def empty_folder(folder):
    filelist = [f for f in os.listdir(folder)]
    for f in filelist:
        os.remove(folder+f)

def copy_folder(src_folder, dst_folder):
    filelist = [f for f in os.listdir(src_folder)]
    for f in filelist:
        shutil.copy(src_folder+f, dst_folder)

if __name__ == "__main__":
    filename = sys.argv[1]
    root = Orgnode.maketree(filename)

    env = Environment(loader=FileSystemLoader('templates'))
    project_template = env.get_template('project.html')
    page_template = env.get_template('page.html')

    empty_folder("output/")
    copy_folder("resources/", "output/")
    make_site(root, project_template, page_template)
