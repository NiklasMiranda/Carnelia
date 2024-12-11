document.addEventListener('DOMContentLoaded', function () {
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

    const track = document.querySelector('.carousel-track');
    const items = document.querySelectorAll('.carousel-item');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    let currentIndex = 0;
    const itemWidth = items[0].offsetWidth;

    function moveCarousel(direction) {
        currentIndex = (currentIndex + direction + items.length) % items.length;
        track.style.transform = `translateX(-${currentIndex * itemWidth}px)`;
    }

    prevBtn.addEventListener('click', () => moveCarousel(-1));
    nextBtn.addEventListener('click', () => moveCarousel(1));

});