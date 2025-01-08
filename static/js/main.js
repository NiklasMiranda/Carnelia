document.addEventListener('DOMContentLoaded', function () {
    console.log('DOMContentLoaded event fired');

    // Navbar functionality
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const mobileMenu = document.querySelector('.mobile-menu');

    hamburgerMenu.addEventListener('click', function() {
        mobileMenu.style.display = mobileMenu.style.display === 'flex' ? 'none' : 'flex';
    });

    // Hero header animation
    const heroHeader = document.querySelector('.hero-header');
    function isInViewport(element) {
        if (!element) return false; // Check if the element exists
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

    if (heroHeader) {
        window.addEventListener('scroll', startAnimation);
        startAnimation();
    }

    // Carousel functionality
    console.log('DOMContentLoaded event fired');

    const rightZone = document.getElementById('right-zone');
    if (rightZone) {
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
            if (radioButtons[index]) {
                radioButtons[index].checked = true;
            }
        }

        if (prevButton && nextButton) {
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
        }

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
    }

    const cookiePopup = document.getElementById('cookie-popup');
    const acceptCookiesButton = document.getElementById('accept-cookies');
    const declineCookiesButton = document.getElementById('decline-cookies'); // Add this line

    if (cookiePopup && acceptCookiesButton && declineCookiesButton) { // Include declineCookiesButton in the check
        if (!document.cookie.includes('cookies_accepted=true')) {
            cookiePopup.style.display = 'block';
        }

        // Accept cookies
        acceptCookiesButton.onclick = function() {
            document.cookie = "cookies_accepted=true; max-age=31536000; path=/"; // Cookie i 1 år
            cookiePopup.style.display = 'none';
        }

        // Decline cookies
        declineCookiesButton.onclick = function() {
            cookiePopup.style.display = 'none';
            // Optionally, you can set a different cookie or perform another action here
            console.log('Cookies declined');
        }
    }
});