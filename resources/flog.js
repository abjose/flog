/* 
NOTE
- can handle URL like
  flog.com/blah?include=woof:dog&exclude=pow:wop:meow&sort=cost&inc=true
TODO
- try out with JS off
- sweep through code, see if things can be simplified with new URL stuff
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

function setFilterState(e, state) {
  e.classList.remove("excluded");
  e.classList.remove("included");
  e.classList.remove("unreachable");
  if (["included", "excluded", "unreachable"].indexOf(state) != -1)
    e.classList.add(state);
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

function initFilters() {
  // for each project, build up object of tags
  // for each tag, add a filter
  // attach on-click
  var projects = document.getElementsByClassName("project");
  var tag_map = getTagMap(projects);
  var tags = Object.keys(tag_map);

  // skip if no filters to show
  if (tags.length == 0) return;

  var filters = document.createElement("div");
  filters.setAttribute("id", "filters");
  filters.innerHTML = "filter by";
  document.getElementById("topbar").appendChild(filters);

  for (var i = tags.length-1; i >= 0; --i) {
    var filter = document.createElement("div");
    filter.innerHTML = tags[i];
    filter.setAttribute("class", "filter");
    show(filter);
    filter.onclick = function() {
      toggleFilter(this.innerHTML);
      filterProjects();
    }

    filters.appendChild(filter);
  }
}

function initProperties() {
  // get all existing properties
  // for each one, add a "property" div to properties
  var properties = getAllProperties();
  if (properties.length == 0) return;  // skip if nothing to show
  var prop_div = document.createElement("div");
  prop_div.setAttribute("id", "properties");
  prop_div.innerHTML = "sort by&nbsp;";
  document.getElementById("topbar").appendChild(prop_div);

  for (var i = 0; i < properties.length; ++i) {
    var property = document.createElement("div");
    property.innerHTML = properties[i];
    property.setAttribute("class", "property");
    // on click, update ordering
    property.onclick = function() {
      toggleOrder(this);
      orderProjects();
    }

    prop_div.appendChild(property);
  }

  // create sorting-direction arrow
  var arrow = document.createElement("div");
  arrow.setAttribute("id", "arrow");
  filters.appendChild(arrow);
}

function filterProjects() {
  // skip if no filters to show
  if (document.getElementById("filters") == undefined) return;

  // get filters and projects
  var params = getURLParameters();
  var include_filters = getIncludeFilters(params);
  var exclude_filters = getExcludeFilters(params);
  var projects = document.getElementsByClassName("project");

  // reset all projects to be visible
  for (var i = 0; i < projects.length; ++i) show(projects[i]);

  // hide any projects that exclude included tags
  for (var i = 0; i < include_filters.length; ++i)
    for (var j = 0; j < projects.length; ++j )
      if (parseTags(projects[j]).indexOf(include_filters[i]) == -1)
        hide(projects[j]);

  // hide any projects that include excluded tags
  for (var i = 0; i < exclude_filters.length; ++i)
    for (var j = 0; j < projects.length; ++j )
      if (parseTags(projects[j]).indexOf(exclude_filters[i]) != -1)
        hide(projects[j]);

  // update filter CSS according to filter status
  var visible_projects = document.getElementsByClassName("visible project");
  var tag_map = getTagMap(visible_projects);
  var filters = document.getElementsByClassName("filter");
  for (var i = 0; i < filters.length; ++i) {
    var filter_text = filters[i].innerHTML;
    if (include_filters.indexOf(filter_text) != -1) {
      setFilterState(filters[i], "included");
    } else if (exclude_filters.indexOf(filter_text) != -1) {
      setFilterState(filters[i], "excluded");
    } else if (!(filter_text in tag_map)) {
      setFilterState(filters[i], "unreachable");
    } else {
      // clear any existing state
      setFilterState(filters[i], "");
    }
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
  var params = getURLParameters();
  var new_property = property.innerHTML;
  var old_property = getOrderProperty(params);
  var increasing = (new_property == old_property)
    ? !isOrderIncreasing(params) : false;

  // update URL with new property
  setOrderProperty(new_property, increasing);
}

function orderProjects() {
  // skip if no properties to show
  if (document.getElementById("properties") == undefined) return;

  // find property to sort by
  var params = getURLParameters();
  var increasing = isOrderIncreasing(params);
  var sort_prop = getOrderProperty(params);
  if (sort_prop == "") sort_prop = "updated";

  // get HTMLCollectionlist of projects, convert to Array, and sort
  var projects = [].slice.call(document.getElementsByClassName("project"));
  projects.sort(getSortFunction(sort_prop));
  if (!increasing) projects = projects.reverse();

  // determine which direction the arrow should point
  var arrow = document.getElementById("arrow");
  if (increasing) {
    arrow.innerHTML = "&#x2b06";
  } else {
    arrow.innerHTML = "&#x2b07";
  }

  // re-insert arrow next to proper property
  var properties = document.getElementsByClassName("property");
  for (var i = 0; i < properties.length; ++i) {
    if (properties[i].innerHTML == sort_prop) {
      properties[i].parentNode.insertBefore(arrow, properties[i].nextSibling);
      break;
    }
  }

  // re-insert the projects in new order
  var projects_div = document.getElementById("projects");
  for (var i = 0; i < projects.length; ++i) {
    // appendChild parent, as want to include wrapping anchor tag
    projects_div.appendChild(projects[i].parentNode);
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
    var a_val = a.attributes["data-"+property] ?
      a.attributes["data-"+property].nodeValue : 0;
        b_val = b.attributes["data-"+property] ?
      b.attributes["data-"+property].nodeValue : 0;
    if (a_val > b_val) return  1;
    if (a_val < b_val) return -1;
    return 0;
  };
}

function getURLParameters() {
  // return an object of key/value pairs based on URL
  var url = window.location.href.split('?');
  if (url.length == 1) return {};
  var params = {};
  var data = url[1].split('&');
  for (var i = 0; i < data.length; ++i) {
    var param = data[i].split('=');
    if (param.length > 1) params[param[0]] = param[1];
  }
  return params;
}

function setURLParameters(params) {
  // remove any empty parameters
  var keys = Object.keys(params);
  for (var i = 0; i < keys.length; ++i) {
    var val = params[keys[i]];
    if (val === undefined || val === "") delete params[keys[i]];
  }
  // update page URL given object of key/value pairs
  var root = window.location.href.split('?')[0];
  var param_strings = [];
  var keys = Object.keys(params);
  for (var i = 0; i < keys.length; ++i) {
    param_strings.push(String(keys[i]) + "=" + String(params[keys[i]]));
  }
  // only add param section if necessary
  if (param_strings.length != 0) root += "?" + param_strings.join('&');
  // replace old URL state
  window.history.replaceState("", "", root);
}

function getIncludeFilters(params) {
  params = params || getURLParameters();
  params = params['include'];
  if (params) return params.split(":");
  return [];
}
function getExcludeFilters(params) {
  params = params || getURLParameters();
  params = params['exclude'];
  if (params) return params.split(":");
  return [];
}

function getOrderProperty(params) {
  return (params || getURLParameters())['sort'] || "";
}
function getOrderDirection(params) {
  return (params || getURLParameters())['inc'] || "";
}
function isOrderIncreasing(params) {
  return getOrderDirection(params) == "true";
}

function setOrderProperty(property, increasing) {
  var params = getURLParameters();
  params['sort'] = property;
  params['inc'] = increasing;
  setURLParameters(params);
}

function toggleFilter(filter) {
  var params = getURLParameters();
  var included = (params['include']) ? params['include'].split(":") : [];
  var excluded = (params['exclude']) ? params['exclude'].split(":") : [];
  var include_idx = included.indexOf(filter);
  var exclude_idx = excluded.indexOf(filter);
  // remove filter from both just in case
  included = remove(included, filter);
  excluded = remove(excluded, filter);
  // now update like nothing=>include=>exclude=>nothing
  if (include_idx != -1) {
    excluded.push(filter);
  } else if (exclude_idx != -1) {
    // do nothing
  } else {
    included.push(filter);
  }
  // update params, and update URL
  params['include'] = included.join(":");
  params['exclude'] = excluded.join(":");
  setURLParameters(params);
}

function remove(array, value){
  // filter value out of passed array
  return array.filter(function(el) { return el !== value; });
}
