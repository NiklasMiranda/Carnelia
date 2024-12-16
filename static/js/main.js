document.addEventListener('DOMContentLoaded', function () {
    console.log('DOMContentLoaded event fired');

    // Navbar functionality
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Hero header animation
    const heroHeader = document.querySelector('.hero-header');
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    function startAnimation() {
        if (isInViewport(heroHeader)) {
            heroHeader.classList.add('animate');
            window.removeEventListener('scroll', startAnimation);
        }
    }

    window.addEventListener('scroll', startAnimation);
    startAnimation();

    // Carousel functionality
    console.log('DOMContentLoaded event fired');

    const rightZone = document.getElementById('right-zone');
    const items = rightZone.querySelectorAll('.content');
    const prevButton = document.querySelector('.carousel-button.prev');
    const nextButton = document.querySelector('.carousel-button.next');
    const totalItems = items.length;
    let currentIndex = 0;

    function showItem(index) {
        console.log('Showing item at index:', index);
        items.forEach((item, i) => {
            if (i === index) {
                item.style.opacity = '1';
                item.style.visibility = 'visible';
            } else {
                item.style.opacity = '0';
                item.style.visibility = 'hidden';
            }
        });
    }

    function updateRadioButtons(index) {
        const radioButtons = document.querySelectorAll('#scene input[type="radio"]');
        radioButtons[index].checked = true;
    }

    prevButton.addEventListener('click', function (event) {
        console.log('Previous button clicked', event);
        currentIndex = (currentIndex === 0) ? totalItems - 1 : currentIndex - 1;
        console.log('New index:', currentIndex);
        showItem(currentIndex);
        updateRadioButtons(currentIndex);
    });

    nextButton.addEventListener('click', function (event) {
        console.log('Next button clicked', event);
        currentIndex = (currentIndex === totalItems - 1) ? 0 : currentIndex + 1;
        console.log('New index:', currentIndex);
        showItem(currentIndex);
        updateRadioButtons(currentIndex);
    });

    // Initialize the carousel by showing the first item
    console.log('Initializing carousel with first item');
    showItem(currentIndex);

    // Add event listeners to radio buttons
    const radioButtons = document.querySelectorAll('#scene input[type="radio"]');
    radioButtons.forEach((radio, index) => {
        radio.addEventListener('change', function() {
            currentIndex = index;
            showItem(currentIndex);
        });
    });

    // Optional: Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            prevButton.click();
        } else if (e.key === 'ArrowRight') {
            nextButton.click();
        }
    });
});