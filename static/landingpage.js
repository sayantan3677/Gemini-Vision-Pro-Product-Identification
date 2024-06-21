document.getElementById('upload-btn').addEventListener('click', function() {
    const fileInput = document.getElementById('upload');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Simulate API call
            setTimeout(() => {
                document.getElementById('result').innerHTML = `<p>Product discovered: Example Product</p>`;
            }, 2000);
        };
        reader.readAsDataURL(file);
    } else {
        alert('Please upload an image file.');
    }
});

document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();
    alert('Message sent!');
    this.reset();
});
