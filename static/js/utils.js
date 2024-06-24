function updateFileName(input) {
    const fileName = input.files[0]?.name;
    const fileNameDisplay = input.parentElement.querySelector('.file-name');
    fileNameDisplay.textContent = fileName || '';
}