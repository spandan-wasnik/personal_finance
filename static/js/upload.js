document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileDisplayArea = document.getElementById('fileDisplayArea');
    const fileNameDisplay = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('border-blue-500', 'bg-blue-50');
        dropZone.classList.remove('border-gray-300');
    }

    function unhighlight(e) {
        dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        dropZone.classList.add('border-gray-300');
    }

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files; // assign to input
            updateFileDisplay();
        }
    }

    // Handle file selection via click
    fileInput.addEventListener('change', updateFileDisplay);

    function updateFileDisplay() {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileNameDisplay.textContent = file.name;
            fileDisplayArea.classList.remove('hidden');
            
            // Check extension
            const validExtensions = ['.csv', '.xls', '.xlsx'];
            const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
            
            if (!validExtensions.includes(fileExt)) {
                alert('Please upload a valid CSV or Excel file.');
                removeFile();
            }
        }
    }

    // Expose globally for the remove button
    window.removeFile = function() {
        fileInput.value = '';
        fileNameDisplay.textContent = '';
        fileDisplayArea.classList.add('hidden');
    }

    // Form submission validation and loading state
    uploadForm.addEventListener('submit', function(e) {
        const sourceSelect = document.getElementById('sourceSelect');
        
        if (fileInput.files.length === 0) {
            e.preventDefault();
            alert('Please select a file to upload.');
            return;
        }
        
        if (!sourceSelect.value) {
            e.preventDefault();
            alert('Please select the source of the statement.');
            sourceSelect.focus();
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
        btnText.textContent = 'Uploading...';
        btnSpinner.classList.remove('hidden');
    });
});
