document.addEventListener("DOMContentLoaded",function(){let e=document.querySelector(".navbar"),t=(window.addEventListener("scroll",function(){50<window.scrollY?e.classList.add("scrolled"):e.classList.remove("scrolled")}),document.querySelector(".hero-header"));function n(){var e;0<=(e=(e=t).getBoundingClientRect()).top&&0<=e.left&&e.bottom<=(window.innerHeight||document.documentElement.clientHeight)&&e.right<=(window.innerWidth||document.documentElement.clientWidth)&&(t.classList.add("animate"),window.removeEventListener("scroll",n))}window.addEventListener("scroll",n),n();let o=document.querySelector(".carousel-track"),r=document.querySelectorAll(".carousel-item");var c=document.querySelector(".prev-btn"),d=document.querySelector(".next-btn");let l=0,i=r[0].offsetWidth;function s(e){l=(l+e+r.length)%r.length,o.style.transform=`translateX(-${l*i}px)`}c.addEventListener("click",()=>s(-1)),d.addEventListener("click",()=>s(1))});