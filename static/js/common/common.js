function showHelpRemoveError(inputElement) {
  inputElement.addEventListener("input", function () {
    // Initialize variables for help and error elements
    let helpElement = null;
    let errorElement = null;

    // Find the next element sibling
    let nextElement = this.nextElementSibling;
    // Loop through the next elements to find help or error elements
    while (nextElement) {
      if (nextElement.classList.contains("help")) {
        helpElement = nextElement;
      }
      if (nextElement.classList.contains("error")) {
        errorElement = nextElement;
      }
      // Exit the loop if both help and error elements are found
      if (helpElement && errorElement) {
        break;
      }
      nextElement = nextElement.nextElementSibling;
    }

    // Display help element if found
    if (helpElement) {
      helpElement.style.display = "block";
    }

    // Remove error element if found
    if (errorElement) {
      errorElement.remove();
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const inputs = document.querySelectorAll("input");
  inputs.forEach(showHelpRemoveError);
});

document.addEventListener("htmx:beforeSwap", function (event) {
  if (event.detail.xhr.status === 400) {
    event.detail.target.innerHTML = JSON.parse(
      event.detail.xhr.responseText
    ).html;
    const inputs = document.querySelectorAll("input");
    inputs.forEach(showHelpRemoveError);
  }
});
