const navbar = document.querySelector(".nav");
const navHambOut = document.querySelector(".hamburger-outside");
const navHambIn = document.querySelector(".hamburger-inside");
const navItems = document.querySelectorAll(".nav-item-cst");

navHambOut.addEventListener("click", () => {
    navHambOut.classList.toggle("active");
    navbar.classList.toggle("active");
});

navHambIn.addEventListener("click", () => {
    navHambIn.classList.toggle("active");
    navbar.classList.toggle("active");
});

function setNavActive(navItem) {
    if (!navItem.classList.contains("active")) {
        const activeItem = document.querySelector(".nav-item-cst.active");
        if (activeItem) {
            activeItem.classList.remove("active");
            const hideElement = document.getElementById(activeItem.dataset.idTarget)
            if (hideElement) hideElement.classList.add('d-none')
        }

        navItem.classList.add("active");
        const showElement = document.getElementById(navItem.dataset.idTarget)

        if (showElement && showElement.classList.contains("d-none")) {
            showElement.classList.remove("d-none");
        }

    }

}

document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.nav-section')) {
        const activeSection = localStorage.getItem('active-section')
        navItems[0].classList.add('active')
        if (activeSection) {
            const activeNavItem = document.querySelector(`.nav-item-cst[data-id-target="${activeSection}"]`)
            setNavActive(activeNavItem)
            localStorage.removeItem('active-section')
        }
    }
})

navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
        e.preventDefault();

        const targetHref = item.querySelector('a').href
        if (window.location.href.split('/').length !== targetHref.split('/').length) {
            localStorage.setItem('active-section', item.dataset.idTarget)
            window.location.assign(targetHref)
        }

        setNavActive(item)

    });
});

document.querySelectorAll('input[type="file"]').forEach((fileInput) => {
    // Create a custom button and filename display span for each file input
    const customButton = document.createElement('label');
    customButton.classList.add('custom-file-upload');
    customButton.textContent = "Choose File";
    customButton.htmlFor = fileInput.id;

    const fileNameSpan = document.createElement('span');
    fileNameSpan.classList.add('file-name');
    fileNameSpan.textContent = "No file chosen";

    // Insert the custom button and filename span before the actual file input
    fileInput.parentNode.insertBefore(customButton, fileInput);
    fileInput.parentNode.insertBefore(fileNameSpan, fileInput.nextSibling);

    // Update filename span on file select
    fileInput.addEventListener('change', function () {
        fileNameSpan.textContent = this.files[0] ? this.files[0].name : "No file chosen";
    });
});
