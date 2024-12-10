document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');

    // Navbar ændrer stil ved scroll
    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    let currentIndex = 0;

    const heroHeader = document.querySelector('.hero-header');

    // Funktion til at tjekke om et element er i viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Funktion til at starte animationen
    function startAnimation() {
        if (isInViewport(heroHeader)) {
            heroHeader.classList.add('animate');
            window.removeEventListener('scroll', startAnimation);
        }
    }

    // Lyt efter scroll event
    window.addEventListener('scroll', startAnimation);

    // Kør også ved load, i tilfælde af at elementet er synligt ved start
    startAnimation();

    // Funktion til at flytte karusellen
    function moveCarousel(direction) {
        const carousel = document.querySelector('.carousel');
        const items = document.querySelectorAll('.carousel-item');
        const totalItems = items.length;

        currentIndex = (currentIndex + direction + totalItems) % totalItems;
        const offset = -currentIndex * 100;
        carousel.style.transform = `translateX(${offset}%)`;
    }

    // Tilføj event listeners for karusel-knapper
    const nextButton = document.querySelector('.carousel-next');
    const prevButton = document.querySelector('.carousel-prev');

    if (nextButton) {
        nextButton.addEventListener('click', function () {
            moveCarousel(1);
        });
    }

    if (prevButton) {
        prevButton.addEventListener('click', function () {
            moveCarousel(-1);
        });
    }



    // Funktion til at tjekke synlighed
    function checkVisibility() {
        const h1Rect = h1Element.getBoundingClientRect();
        const pRect = pElement.getBoundingClientRect();
        const windowHeight = window.innerHeight;

        if (h1Rect.top < windowHeight && h1Rect.bottom >= 0) {
            h1Element.classList.add('visible');
        }

        if (pRect.top < windowHeight && pRect.bottom >= 0) {
            pElement.classList.add('visible');
        }
    }

    // Kald funktionen ved scroll og load
    window.addEventListener('scroll', checkVisibility);
    window.addEventListener('load', checkVisibility);

    const pictureSection = document.querySelector('.picture-section');
    const pictureImg = document.querySelector('.picture-img');
    const pictureText = document.querySelector('.picture-text');

    // Brug Intersection Observer API til at detektere når sektionen er synlig
    const pictureObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Når sektionen er synlig, aktiver fade-in effekten
                pictureImg.classList.add('fade-in');
                pictureText.classList.add('fade-in');
            }
        });
    }, { threshold: 0.5 }); // Observer sektionen når 50% af den er synlig

    // Begynd at observere picture-section
    pictureObserver.observe(pictureSection);

    const sliderTrack = document.querySelector('.slider-track');
    const items = Array.from(document.querySelectorAll('.slider-item'));
    let totalWidth = 0;

    // Beregn samlet bredde af items
    items.forEach((item) => {
        totalWidth += item.offsetWidth;
    });

    // Gentag items for sømløs rulning
    while (totalWidth < window.innerWidth * 2) {
        items.forEach((item) => {
            const clone = item.cloneNode(true);
            sliderTrack.appendChild(clone);
            totalWidth += item.offsetWidth;
        });
    }

    // Stop animation ved hover
    sliderTrack.addEventListener('mouseenter', () => {
        sliderTrack.classList.add('paused');
    });

    sliderTrack.addEventListener('mouseleave', () => {
        sliderTrack.classList.remove('paused');
    });

    const slides = document.querySelector('.carousel-slides');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    let index = 0;
    const totalSlides = slides.querySelectorAll('.carousel-slide').length;

    nextBtn.addEventListener('click', () => {
        index = (index + 1) % totalSlides;
        updateCarousel();
    });

    prevBtn.addEventListener('click', () => {
        index = (index - 1 + totalSlides) % totalSlides;
        updateCarousel();
    });

    function updateCarousel() {
        const slideWidth = slides.querySelector('img').clientWidth;
        slides.style.transform = `translateX(-${index * slideWidth}px)`;
    }

    // Target sektionen og elementerne
    const textSection = document.querySelector('.text-block'); // Hele sektionen
    const animatedText = document.querySelectorAll('.animated-text'); // Teksten
    const viewButton = document.querySelector('.view-button'); // Knappen

    // Brug Intersection Observer API til at detektere når sektionen er synlig
    const textObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Når sektionen er synlig, aktiver fade-in effekten
                animatedText.forEach(el => el.classList.add('fade-in'));
                viewButton.classList.add('fade-in');

                // Fade-in sektionen
                textSection.classList.add('fade-in');
            }
        });
    }, { threshold: 0.5 }); // Observer sektionen når 50% af den er synlig

    // Begynd at observere text-block sektionen
    textObserver.observe(textSection);
});
