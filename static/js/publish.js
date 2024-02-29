document.addEventListener("DOMContentLoaded", function () {
  const submitFormButton = document.querySelector("#submit-publish");
  const fileInput = document.querySelector("#fileInput");

  function submitForm(event) {
    event.preventDefault();

    const title = document.querySelector("#title").value;
    const authors = document.querySelector("#authors").value;
    const publicationDate = document.querySelector("#yearInput").value;
    const thesisAdvisor = document.querySelector("#thesisAdvisor").value;
    const department = document.querySelector("#department").value;
    const degree = document.querySelector("#degree").value;
    const subjectArea = document.querySelector("#subjectArea").value;
    const subjectCode = document.querySelector("#subjectCode").value;
    const abstract = document.querySelector("#abstract").value;
    const file = fileInput.files[0];

    // Check if any required field is empty
    if (!title || !authors || !publicationDate || !thesisAdvisor || !department || !degree || !subjectArea || !subjectCode || !abstract || !file) {
      alert("Please fill in all fields and select a file.");
      return; // Stop form submission if any field is missing
    }

    // Check if the selected file is a DOCX or PDF
    if (file.type !== "application/pdf") {
      alert("Please select a PDF file.");
      return; // Stop form submission if the file is not a DOCX or PDF
    }

    const formData = new FormData();
    formData.append("title", title);
    formData.append("authors", authors);
    formData.append("publicationDate", publicationDate);
    formData.append("thesisAdvisor", thesisAdvisor);
    formData.append("department", department);
    formData.append("degree", degree);
    formData.append("subjectArea", subjectArea);
    formData.append("subjectCode", subjectCode);
    formData.append("abstract", abstract);
    formData.append("file", file);

    fetch("/submit_data", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.text())
      .then((data) => {
        // Handle any response data if needed
        alert("Upload successful!");
        window.location.href = "/"; // Redirect to abstract.html
      })
      .catch((error) => {
        // Handle any errors that occurred during the request
        console.error("Error:", error);
      });
  }

  submitFormButton.addEventListener("click", submitForm);
});



$(document).ready(function() {
  // Check session state on page load
  $.getJSON("/session_state", function(data) {
    if (!data.isLoggedIn) {
      window.location.href = "/"; // Redirect to index.html
    }
  });
});

// Function to update the year input value without the month
function updateYearInputValue() {
  const monthInput = document.getElementById('yearInput');
  const year = monthInput.value.slice(0, 4); // Extract the year from the input value
  monthInput.value = year;
}

// Attach the updateYearInputValue function to the change event of the month input
document.getElementById('yearInput').addEventListener('change', updateYearInputValue);


const submitButton = document.getElementById('submit-publish');
const pocContainer = document.getElementById('poc-container');

submitButton.addEventListener('click', function(event) {
  console.log('clicked');
  pocContainer.classList.toggle('hidden');
});



$(document).ready(function() {
  $.getJSON('/get_departments', function(data) {
      // Populate the department dropdown with the data received from the server
      $('#department').empty().append('<option selected disabled>Select Department</option>');
      $.each(data, function(i, department) {
          $('#department').append('<option value="' + department + '">' + department + '</option>');
      });
  });
});

$('#department').change(function() {
  var department = $(this).val();
  $.getJSON('/get_degrees/' + department, function(data) {
      // Populate the degree dropdown with the data received from the server
      $('#degree').empty().append('<option selected disabled>Select Degree</option>');
      $.each(data, function(i, degree) {
          $('#degree').append('<option value="' + degree + '">' + degree + '</option>');
      });
      $('#degree').prop('disabled', false); // Enable the degree dropdown
  });
});

$('#degree').change(function() {
  var department = $('#department').val();
  var degree = $(this).val();
  $.getJSON('/get_subject_areas/' + department + '/' + degree, function(data) {
      // Populate the subject area dropdown with the data received from the server
      $('#subjectArea').empty().append('<option selected disabled>Select Subject Area</option>');
      $.each(data, function(i, subjectArea) {
          $('#subjectArea').append('<option value="' + subjectArea + '">' + subjectArea + '</option>');
      });
      $('#subjectArea').prop('disabled', false); // Enable the subject area dropdown
  });
});

$('#subjectArea').change(function() {
  $('#subjectCode').prop('disabled', false); // Enable the subject code dropdown
});
