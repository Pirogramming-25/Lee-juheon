document.addEventListener("DOMContentLoaded", () => {
    const toggleButtons = document.querySelectorAll(
        ".js-password-toggle"
    );

    toggleButtons.forEach((button) => {
        const wrapper = button.closest(
            ".password-field-wrapper"
        );

        const input = wrapper.querySelector(
            ".js-password-input"
        );

        button.addEventListener("click", () => {
            const isHidden = input.type === "password";

            input.type = isHidden ? "text" : "password";

            button.classList.toggle("is-visible", isHidden);

            button.setAttribute(
                "aria-label",
                isHidden ? "비밀번호 숨기기" : "비밀번호 표시"
            );
        });
    });
});
