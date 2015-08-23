/* TODO
- use colons instead of spaces to delimit tags
- nice if had filters in URL bar so could "deep link"?
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
  // Expects tags in format "tag1:tag2", return ["tag1", "tag2"].
  var tags = project.attributes["data-tags"].value.split(":");
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

  var filters = document.createElement("div");
  filters.setAttribute("id", "filters");
  document.getElementById("topbar").appendChild(filters);

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

  // then, for visible projects,
  // get their tags (into an object)
  // update visibility
  var visible_projects = document.getElementsByClassName("visible project");
  var tag_map = getTagMap(visible_projects);
  var filters = document.getElementsByClassName("filter");
  for (var i = 0; i < filters.length; ++i) {
    filters[i].innerHTML in tag_map ?
      show(filters[i]) : hide(filters[i]);
  }
}

function getAllProperties() {
  // return a list of all existing properties
  var properties = {};
  var projects = document.getElementsByClassName("project");
  for (var i = 0; i < projects.length; ++i) {
    var project_properties = Object.keys(parseProperties(projects[i]));
    for (var j = 0; j < project_properties.length; ++j) {
      properties[project_properties[j]] = true;
    }
  }
  return Object.keys(properties);
}

function parseProperties(project) {
  // make a property key-value object for given project
  var properties = {};
  for (var i = 0; i < project.attributes.length; ++i) {
    var key = project.attributes[i].nodeName;
    if (key.substring(0, 5) == "data-" && key.indexOf("tags") == -1) {
      properties[key.substring(5)] = project.attributes[key];
    }
  }
 return properties;
}

function toggleOrder(property) {
  // determine which direction the arrow should point
  var arrow = document.getElementById("arrow");
  if (!property.classList.contains("sort-decreasing")) {
    arrow.innerHTML = "&#x2b07";
    property.classList.add("sort-decreasing");
    property.classList.remove("sort-increasing");
  } else {
    arrow.innerHTML = "&#x2b06";
    property.classList.add("sort-increasing");
    property.classList.remove("sort-decreasing");
  }

  // remove old arrow, re-insert arrow to be next to property
  property.parentNode.insertBefore(arrow, property.nextSibling);

  // clear old property of sorting-related class
  var inc = document.getElementsByClassName("sort-increasing");
  var dec = document.getElementsByClassName("sort-decreasing");
  for (var i = 0; i < inc.length; ++i)
    if (inc[i] !== property) inc[i].classList.remove("sort-increasing");
  for (var i = 0; i < dec.length; ++i)
    if (dec[i] !== property) dec[i].classList.remove("sort-decreasing");
}

function initProperties() {
  // get all existing properties
  // for each one, add a "property" div to filters (rename?)
  var properties = getAllProperties();
  var filters = document.getElementById("filters");
  for (var i = 0; i < properties.length; ++i) {
    var property = document.createElement("div");
    property.innerHTML = properties[i];
    property.setAttribute("class", "property");
    // on click, update ordering
    property.onclick = function() {
      toggleOrder(this);
      orderProjects();
    }

    filters.appendChild(property);
  }

  // sort descending by date initially
  var default_property = "updated";
  var arrow = document.createElement("div");
  arrow.setAttribute("id", "arrow");
  filters.appendChild(arrow);
  var properties = document.getElementsByClassName("property");
  for (var i = 0; i < properties.length; ++i) {
    if (properties[i].innerHTML == default_property) {
      toggleOrder(properties[i]);
      break;
    }
  }
}

function orderProjects() {
  // find property to sort by
  var increasing = true;
  var sort_prop = document.getElementsByClassName("sort-increasing");
  if (sort_prop.length == 0) {
    increasing = false;
    sort_prop = document.getElementsByClassName("sort-decreasing");
  }
  if (sort_prop.length == 0) {
    console.log("Couldn't find property to sort by");
    return;
  }
  sort_prop = sort_prop[0].innerHTML;

  // get HTMLCollectionlist of projects, convert to Array, and sort
  var projects = [].slice.call(document.getElementsByClassName("project"));
  projects.sort(getSortFunction(sort_prop));
  if (!increasing) projects = projects.reverse();

  // re-insert the projects in new order
  var projects_div = document.getElementById("projects");
  for (var i = 0; i < projects.length; ++i) {
    // appendChild parent, as want to include wrapping anchor tag
    projects_div.appendChild(projects[i].parent);
  }
}

function getSortFunction(property) {
  // special case sorting functions
  var sort_functions = {};

  if (property in sort_functions) return sort_functions[property]
  return sortByProperty(property);
}

function sortByProperty(property) {
  return function(a, b) {
    var a_val = a.attributes["data-"+property].nodeValue,
        b_val = b.attributes["data-"+property].nodeValue;
    if (a_val > b_val) return  1;
    if (a_val < b_val) return -1;
    return 0;
  };
}
