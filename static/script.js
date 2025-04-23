let btn = document.querySelector('#btn');
let sidebar = document.querySelector('.sidebar');
let searchBtn = document.querySelector('.bx-search');
let listItem = document.querySelectorAll('.list-item');

btn.onclick = function() {
    sidebar.classList.toggle('active');
}

searchBtn.onclick = function() {
    sidebar.classList.toggle('active');
}

function activeLink() {
    listItem.forEach(item => item.classList.remove('active'));
    this.classList.add('active');
}

listItem.forEach(item => item.onclick = activeLink);

const imageInput = document.getElementById('image-input');
const cartoonifyButton = document.getElementById('cartoonify-button');
const originalImage = document.getElementById('original-image');
const cartoonImage = document.getElementById('cartoon-image');

// Display the original image when selected
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            originalImage.src = event.target.result;
            originalImage.style.display = 'block'; // Show the original image
            cartoonImage.style.display = 'none'; // Hide the cartoon image initially
        };
        reader.readAsDataURL(file);
    }
});

// Handle cartoonify button click
cartoonifyButton.addEventListener('click', (event) => {
    event.preventDefault(); // Prevent default form submission

    if (imageInput.files.length === 0) {
        alert('Please select an image first.');
        return;
    }

    // Show loading state
    cartoonifyButton.disabled = true;
    cartoonifyButton.textContent = 'Processing...';

    const formData = new FormData();
    formData.append('image', imageInput.files[0]);

    fetch('/cartoonify', {
        method: 'POST',
        body: formData,
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then((blob) => {
        const url = URL.createObjectURL(blob);
        cartoonImage.src = url;
        cartoonImage.style.display = 'block'; // Show the cartoon image
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while cartoonizing the image. Please try again.');
    });
});