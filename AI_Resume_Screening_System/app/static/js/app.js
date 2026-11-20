document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.querySelector('input[type="file"][name="resumes"]');
  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const count = fileInput.files.length;
      const help = document.getElementById("selected-files");
      if (help) help.textContent = count ? `${count} file(s) selected` : "";
    });
  }
});
