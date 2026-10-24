document.addEventListener("DOMContentLoaded", function () {


    // =================================================
    // CURRENT YEAR
    // =================================================

    const yearElement =
        document.getElementById("currentYear");

    if (yearElement) {

        yearElement.textContent =
            new Date().getFullYear();

    }



    // =================================================
    // NAVBAR SCROLL EFFECT
    // =================================================

    const navbar =
        document.getElementById("mainNavbar");


    function updateNavbar() {

        if (!navbar) {
            return;
        }


        if (window.scrollY > 40) {

            navbar.classList.add("scrolled");

        } else {

            navbar.classList.remove("scrolled");

        }

    }


    updateNavbar();


    window.addEventListener(
        "scroll",
        updateNavbar,
        { passive: true }
    );



    // =================================================
    // SCROLL REVEAL
    // =================================================

    const revealElements =
        document.querySelectorAll(".reveal");


    const revealObserver =
        new IntersectionObserver(

            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "visible"
                        );

                        observer.unobserve(
                            entry.target
                        );

                    }

                });

            },

            {
                threshold: 0.12
            }

        );


    revealElements.forEach(function (element) {

        revealObserver.observe(element);

    });



    // =================================================
    // CLOSE MOBILE NAVBAR AFTER CLICK
    // =================================================

    const navLinks =
        document.querySelectorAll(
            "#navbarMenu .nav-link"
        );


    const navbarMenu =
        document.getElementById("navbarMenu");


    navLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function () {

                if (
                    window.innerWidth < 992 &&
                    navbarMenu &&
                    navbarMenu.classList.contains("show")
                ) {

                    const collapse =
                        bootstrap.Collapse.getOrCreateInstance(
                            navbarMenu
                        );

                    collapse.hide();

                }

            }
        );

    });


});