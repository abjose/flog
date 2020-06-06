import Orgnode, datetime, markdown, sys, os, shutil
from jinja2 import Environment, FileSystemLoader

"""
TODO:
- check that no sections have the same heading
- put a heading on each page?
- allow user to specify another resources/ directory
- get root to be 'index.html' while still allowing you to use title
"""

def make_site(title, root, project_template, page_template):
    if root.hasTag("private"): return
    write_page(root.URL(), get_page(title, root, project_template,
                                    page_template))
    if not root.hasTag("leaf"):
        for child in root.children:
            make_site(title, child, project_template, page_template)

def write_page(url, content):
    filename = "html/" + url
    with open(filename, "w") as f:
        f.write(content)

def get_page(title, node, project_template, page_template):
    projects = get_projects(node, project_template)
    content = get_content(node)
    return page_template.render(title=title, node=node, projects=projects,
                                content=content)

def get_content(node):
    content = node.LeafContent() if node.hasTag("leaf") else node.Body()
    content = content.strip()
    return markdown.markdown(content)

def get_projects(node, project_template):
    if node.hasTag("leaf"): return []
    return [project_template.render(node=child) for child in node.children
            if not child.hasTag("private")]

def empty_folder(folder):
    if not os.path.exists(folder): os.makedirs(folder)
    filelist = [f for f in os.listdir(folder)]
    for f in filelist:
        os.remove(folder+f)

def copy_folder(src_folder, dst_folder):
    try:
        filelist = [f for f in os.listdir(src_folder)]
        for f in filelist:
            shutil.copy(src_folder+f, dst_folder)
    except:
        print(f"Couldn't copy {src_folder} to {dst_folder}, continuing...")

if __name__ == "__main__":
    flog_path = os.path.split(sys.argv[0])[0]
    if flog_path: flog_path += "/"
    org_filename = sys.argv[1]
    title = org_filename.split(".")[0]
    root = Orgnode.maketree(title, org_filename)

    env = Environment(loader=FileSystemLoader(flog_path + "templates"))
    project_template = env.get_template("project.html")
    page_template = env.get_template("page.html")

    empty_folder("html/")
    # copy user-specified resources over
    copy_folder("resources/", "html/")
    # copy the flog resources over (be careful of overwriting)
    copy_folder(flog_path + "resources/", "html/")
    make_site(title, root, project_template, page_template)
