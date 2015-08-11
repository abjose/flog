/* TODO
- ADD SORTING STUFF THEN STOP AND WORK ON org-to-html part
- use colons instead of spaces to delimit tags
- figure out what things will look like if both text and projects
- nice if had filters in URL bar so could "deep link"?
- expose properties / sort stuff by properties
  use flexbox? 
  https://news.ycombinator.com/item?id=9963714
  https://css-tricks.com/snippets/css/a-guide-to-flexbox/
  https://philipwalton.github.io/solved-by-flexbox/demos/grids/
- have different js (or none) for "content" page (project)
- try out with JS off
*/

initFilters();
initProperties();
filterProjects();
orderProjects()

function hide(e) {
  e.classList.add("hidden");
  e.classList.remove("visible");
}

function show(e) {
  e.classList.add("visible");
  e.classList.remove("hidden");
}

function toggleSelected(filter) {
  filter.classList.toggle("selected");
}

function parseTags(project) {
  // Expects tags in format "tag1 tag2", return ["tag1", "tag2"].
  var tags = project.attributes["data-tags"].value.split(" ");
  if (tags[0] == "") return [];
  return tags;
}

function getTagMap(projects) {
  var tag_map = {};
  for (var i = 0; i < projects.length; ++i) {
    var tags = parseTags(projects[i]);
    for (var j = 0; j < tags.length; ++j) {
      tag_map[tags[j]] = true;
    }
  }

  return tag_map;
}

function getFilterContent(filters) {
  var content = [];
  for (var i = 0; i < filters.length; ++i) {
    content.push(filters[i].innerHTML);
  }
  return content;
}

function initFilters() {
  // for each project, build up object of tags
  // for each tag, add a filter
  // attach on-click
  var projects = document.getElementsByClassName("project");
  var tag_map = getTagMap(projects);
  var tags = Object.keys(tag_map);

  var filters = document.getElementById("filters");
  for (var i = 0; i < tags.length; ++i) {
    var filter = document.createElement("div");
    filter.innerHTML = tags[i];
    filter.setAttribute("class", "filter");
    show(filter);
    filter.onclick = function() {
      toggleSelected(this);
      filterProjects();
    }

    filters.appendChild(filter);
  }
}

function filterProjects() {
  // get all selected filters
  // for each project, for each selected filter,
  // if doesn't have one, hide
  var selected_filters = document.getElementsByClassName("selected filter");
  selected_filters = getFilterContent(selected_filters);
  var projects = document.getElementsByClassName("project");
  for (var i = 0; i < projects.length; ++i) {
    var project_tags = parseTags(projects[i]);
    var should_show = true;
    if (selected_filters.length > 0) {
      for (var j = 0; j < selected_filters.length; ++j) {
        if (project_tags.indexOf(selected_filters[j]) == -1) {
          should_show = false;
          break;
        }
      }
    }
    should_show ? show(projects[i]) : hide(projects[i]);
  }

    if (is_visible) {
      for (var j = 0; j < tags.length; ++j) {
	visible_filters[tags[j]] = true;
      }
    }
  }

  // Only show filters that should be visible.
  var filter_elements = document.getElementsByClassName("filter");
  var visible_filters = Object.keys(visible_filters);
  for (var i = 0; i < filter_elements.length; ++i) {
    var filter = filter_elements[i];
    if (visible_filters.indexOf(filter.innerHTML) == -1) {
      filter.style.display = "none";
    } else {
      filter.style.display = "block";
    }
  }
}

function updateProjects(property, isAscending) {
  // Render the projects, given tags that should be visible and 
  // a property to sort by.
  var projects = document.getElementsByClassName("project");
  for (var i = 0; i < projects.length; ++i) {
    // Show a project only if it has all specified tags.
    var project = projects[i];    
    var tags = parseTags(project);
    var display = "block";
    for (var j = 0; j < filters.length; ++j) {
      if (tags.indexOf(filters[j]) == -1) {
	display = "none";
	break;
      }
    }
    project.style.display = display;
  }
}

function parseTags(e) {
  // Expects tags in format "tag1 tag2", return ["tag1", "tag2"].
  var tags = e.attributes["tags"].value.split(" ");
  if (tags[0] == "") return [];
  return tags;
}
