import Orgnode, datetime, markdown, sys, os, shutil
from jinja2 import Environment, FileSystemLoader

"""
TODO:
-
"""

def make_site(title, node, project_template, page_template):
    if node.hasTag("private"): return
    write_page(node.URL(), get_page(title, node, project_template,
                                    page_template))
    if not node.hasTag("leaf"):
        for child in node.children:
            make_site(title, child, project_template, page_template)

def write_page(url, content):
    path = "html/" + url
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, "w") as f:
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
    shutil.rmtree(folder)
    os.makedirs(folder)

def copy_folder(src_folder, dst_folder):
    try:
        filelist = [f for f in os.listdir(src_folder)]
        for f in filelist:
            shutil.copy(src_folder+f, dst_folder)
    except:
        print(f"Couldn't copy {src_folder} to {dst_folder}, continuing...")

# Check the children of each node have unique names to avoid naming collisions.
def verify_child_uniqueness(node):
    child_names = [child.Heading() for child in node.children]
    if len(child_names) != len(set(child_names)):
        print(f"Error: Duplicate child found on page '{node.Heading()}', please rename.")
        return False
    return all(map(verify_child_uniqueness, node.children))

# Return False if a check failed, otherwise true
def verify_tree(tree):
    if not verify_child_uniqueness(tree):
        return False
    return True

if __name__ == "__main__":
    flog_path = os.path.split(sys.argv[0])[0]
    if flog_path: flog_path += "/"
    org_filename = sys.argv[1]
    title = org_filename.split(".")[0]
    root = Orgnode.maketree(title, org_filename)
    if not verify_tree(root):
        print("Quitting early, please fix errors to proceed.")
        sys.exit(0)

    env = Environment(loader=FileSystemLoader(flog_path + "templates"))
    project_template = env.get_template("project.html")
    page_template = env.get_template("page.html")

    empty_folder("html/")
    # copy user-specified resources over
    copy_folder("resources/", "html/")
    # copy the flog resources over (be careful of overwriting)
    copy_folder(flog_path + "resources/", "html/")
    make_site(title, root, project_template, page_template)
