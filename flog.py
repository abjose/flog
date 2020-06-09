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

# Not currently used.
def verify_child_uniqueness(node):
    child_names = [child.Heading() for child in node.children]
    if len(child_names) != len(set(child_names)):
        print(f"Error: Duplicate child found on page '{node.Heading()}', please rename.")
        return False
    return all(map(verify_child_uniqueness, node.children))

# Check urls are unique to avoid overwriting.
# TODO: handle this better; previously tried making directory structure reflect tree but
#       it's kind of annoying.
def verify_url_uniqueness(node):
    def get_urls(node):
        if node.hasTag("private"): return []
        if node.hasTag("leaf"): return [node.URL()]
        descendant_urls = [item for sublist in map(get_urls, node.children)
                           for item in sublist]
        return [node.URL()] + descendant_urls

    seen = dict()
    no_dupes = True
    for url in get_urls(node):
        if url not in seen:
            seen[url] = 1
        else:
            no_dupes = False
            seen[url] += 1
            if seen[url] == 2:
                print(f"Error: Duplicate url '{url}', please rename.")

    return no_dupes

# Check that all children of a node share same properties.
def verify_children_share_properties(node):
    if not node.children:
        return True

    child0_props = set(node.children[0].properties.keys())
    for child in node.children[1:]:
        verify_children_share_properties(child)
        child_props = set(child.properties.keys())
        if child_props != child0_props:
            print(f"Warning: A child of '{node.Heading()}' ('{child.Heading()}' or " +
                  f"'{node.children[0].Heading()}') is missing a common property.")
            return False
    return True

# Return False if a check failed, otherwise true
def verify_tree(tree):
    if not verify_url_uniqueness(tree):
        return False

    # Just warn about this for now
    verify_children_share_properties(tree)

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
