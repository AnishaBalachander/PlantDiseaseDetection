document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const resultSection = document.querySelector(".result");
    const captureButton = document.getElementById("capture-button");
    const fileInput = document.getElementById("file-input");

    // Initialize FormData object
    let formData = new FormData();

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        // Check if a new image has been captured
        if (captureButton.classList.contains("active")) {
            // Make a POST request to the "/predict" endpoint
            fetch("/predict", {
                method: "POST",
                body: formData, // Use the formData object with the captured image
            })
            .then(response => response.json())
            .then(data => {
                // Update the result section with the received data
                updateResult(data);
            })
            .catch(error => {
                console.error("Error:", error);
            });
        } else {
            // Make a POST request to the "/predict" endpoint with the uploaded image
            fetch("/predict", {
                method: "POST",
                body: formData, // Use the formData object with the uploaded image
            })
            .then(response => response.json())
            .then(data => {
                // Update the result section with the received data
                updateResult(data);
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });

    // Function to update the result section
    function updateResult(data) {
        const diseaseElement = document.getElementById("disease");
        const confidenceElement = document.getElementById("confidence");
        const symptomsElement = document.getElementById("symptoms");
        const curesElement = document.getElementById("cures");

        diseaseElement.textContent = "Disease🦠: " + data.class;
        confidenceElement.textContent = "Confidence💯: " + data.confidence;
        symptomsElement.textContent = "Symptoms📖: " + data.symptoms;
        curesElement.textContent = "Cures💊: " + data.cures;
    }

    // Event listener for capturing an image from the webcam
    captureButton.addEventListener("click", function () {
        // Make a POST request to the "/capture_image" endpoint
        // Declare formData here so it's accessible in both then blocks
        const formData = new FormData();
        fetch("/capture_image", {
            method: "POST",
        })
        .then(response => response.json())
        .then(data => {
            
            if (data.error) {
                console.error(data.error);
            } else if (data.image_base64) {
                // Create a FileReader to read the selected image file
            const reader = new FileReader();

                // Display the captured image
                const imageContainer = document.getElementById("image-container");
                imageContainer.innerHTML = `<img src="data:image/jpeg;base64, ${data.image_base64}" alt="Captured Image">`;
                // Set the "Capture Image" button as active
                captureButton.classList.add("active");  
                // Convert the base64 image to a Blob
                const byteCharacters = atob(data.image_base64);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: 'image/jpeg' });

                // Create a new File from the Blob
                const capturedFile = new File([blob], "captured_image.jpg", { type: "image/jpeg" });

                // Remove any previously uploaded image
                fileInput.value = "";
                 // Read the image file as a data URL
            reader.readAsDataURL(capturedFile);
    
                // Create a FormData object with the captured image
                formData.set("file", capturedFile);
                console.log("Image Captured",capturedFile)
            }
        })
        .then(()=>{
            fetch("/predict", {
                method: "POST",
                body: formData, // Use the formData object with the uploaded image
            })
            .then(response => response.json())
            .then(data => {
                // Update the result section with the received data
                updateResult(data);
            })
            .catch(error => {
                console.error("Error:", error);
            });
        })
    });

    // Event listener for handling file input for image upload
    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            // Create a FileReader to read the selected image file
            const reader = new FileReader();

            reader.onload = function () {
                // Display the uploaded image
                const imageContainer = document.getElementById("image-container");
                imageContainer.innerHTML = `<img src="${reader.result}" alt="Uploaded Image">`;
                // Remove the "active" class from the "Capture Image" button
                captureButton.classList.remove("active");
            };

            // Read the image file as a data URL
            reader.readAsDataURL(file);

            // Set the uploaded image as a file in the formData object
            formData.set("file", file);
        }
    });
});

// Function to convert a data URI to a Blob object
function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(",")[1]);
    const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);

    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ab], { type: mimeString });
}