document.addEventListener("DOMContentLoaded", () => {
    const welcomeMessage = document.getElementById("saludo");

    if (welcomeMessage) {
        setTimeout(() => {
            welcomeMessage.classList.add("fade-out");

            setTimeout(() => {
                welcomeMessage.remove();
            }, 1000); 
        }, 10000); 
    }
});
