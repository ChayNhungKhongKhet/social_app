function showHelpRemoveError(inputElement) {
  inputElement.addEventListener("input", function () {
    let helpElement = this.nextElementSibling.nextElementSibling;
    if (helpElement && helpElement.classList.contains("help")) {
      helpElement.style.display = "block";
    }
    let errorElement = this.nextElementSibling;
    if (errorElement && errorElement.classList.contains("error")) {
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
