/* TODO
- use colons instead of commas to delimit tags
*/

var filters = [];
initFilters();
updateProjects("date", false);
updateFilters();

function initFilters() {
  var filters = document.getElementsByClassName("filter");
  for (var i = 0; i < filters.length; ++i) {
    var filter = filters[i];
    filter.onclick = function() {
      toggleFilter(this);
    }
  }
}

function toggleFilter(filter) {
  var index = filters.indexOf(filter.innerHTML);
  if (index !== -1) {
    filter.style.fontWeight = "";
    filters.splice(index, 1);
  } else {
    filter.style.fontWeight = "bold";
    filters.push(filter.innerHTML);
  }
  updateFilters();
  updateProjects("date", false);
}

function onPropertyChange() {
}

function onSortOrderChange() {
}

function updateFilters() {
  // Only show "possible" filters.
  // TODO: don't repeat yourself.

  var visible_filters = {};
  // Accumulate visible filters.
  var projects = document.getElementsByClassName("project");
  for (var i = 0; i < projects.length; ++i) {
    var project = projects[i];    
    var tags = parseTags(project);
    var is_visible = true;

    for (var j = 0; j < filters.length; ++j) {
      if (tags.indexOf(filters[j]) == -1) {
	is_visible = false;
	break;
      }
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
