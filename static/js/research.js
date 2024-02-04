document.getElementById('search-button').addEventListener('click', function () {
  performSearch();
});

function performSearch() {
  const searchQuery = document.getElementById('search-input').value;

  let url = '/research?';
  if (searchQuery) {
      url += `search=${encodeURIComponent(searchQuery)}&`;
  }

  window.location.href = url;
}

document.addEventListener("DOMContentLoaded", function() {
  // Initialize Quill editor
  var quill = new Quill('#editor', {
      theme: 'snow',
      readOnly: true  // Set to true if you only want to display the content
  });

  // Get the content from the Flask variable passed in the template
  var content = {{ content|tojson|safe }};
  
  // Update Quill editor with the content
  quill.clipboard.dangerouslyPasteHTML(content);
});