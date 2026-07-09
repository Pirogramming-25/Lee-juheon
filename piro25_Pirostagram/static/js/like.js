document.addEventListener("DOMContentLoaded", () => {
    const OUTLINE_HEART = `
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M16.792 3.904C18.1064 3.97667 19.3389 4.56591 20.2207 5.54331C21.1026 6.52071 21.5624 7.80705 21.5 9.122C21.5 12.194 18.848 14.081 16.303 16.344C13.791 18.587 12.438 19.813 12 20.096C11.523 19.787 9.857 18.273 7.697 16.344C5.141 14.072 2.5 12.167 2.5 9.122C2.43756 7.80705 2.89739 6.52071 3.77926 5.54331C4.66113 4.56591 5.89357 3.97667 7.208 3.904C7.93614 3.88193 8.65756 4.04919 9.30171 4.3894C9.94586 4.72962 10.4907 5.23117 10.883 5.845C11.723 7.02 11.863 7.608 12.003 7.608C12.143 7.608 12.281 7.02 13.113 5.842C13.5031 5.22533 14.0481 4.7218 14.6937 4.38172C15.3393 4.04164 16.0628 3.87691 16.792 3.904ZM16.792 1.904C15.8839 1.87493 14.981 2.05109 14.1504 2.41935C13.3199 2.78762 12.5831 3.33851 11.995 4.031C11.4074 3.34053 10.6721 2.79091 9.84354 2.42276C9.01498 2.0546 8.11428 1.87732 7.208 1.904C5.36287 1.97615 3.62138 2.77599 2.36434 4.1286C1.1073 5.48121 0.436992 7.27654 0.499998 9.122C0.499998 12.732 3.05 14.949 5.515 17.092C5.798 17.338 6.084 17.586 6.368 17.839L7.395 18.757C8.51504 19.8228 9.68926 20.8301 10.913 21.775C11.2368 21.9846 11.6143 22.0962 12 22.0962C12.3857 22.0962 12.7632 21.9846 13.087 21.775C14.3497 20.8013 15.56 19.7615 16.713 18.66L17.635 17.836C17.928 17.576 18.225 17.317 18.52 17.062C20.854 15.037 23.5 12.742 23.5 9.122C23.563 7.27654 22.8927 5.48121 21.6357 4.1286C20.3786 2.77599 18.6371 1.97615 16.792 1.904Z"></path>
        </svg>
    `;

    const FILLED_HEART = `
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35Z"></path>
        </svg>
    `;

    const likeForms = document.querySelectorAll(".like-form");

    likeForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const postId = form.dataset.postId;
            const button = form.querySelector(".like-button");
            const iconContainer = form.querySelector(".like-icon");
            const countElement = document.querySelector(
                `#like-count-${postId}`
            );

            button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                if (!response.ok) {
                    throw new Error("좋아요 요청 실패");
                }

                const data = await response.json();

                button.classList.toggle(
                    "is-liked",
                    data.liked
                );

                if (iconContainer) {
                    iconContainer.innerHTML = data.liked
                        ? FILLED_HEART
                        : OUTLINE_HEART;
                }

                if (countElement) {
                    countElement.textContent = data.like_count;
                }
            } catch (error) {
                alert("좋아요 처리 중 오류가 발생했습니다.");
                console.error(error);
            } finally {
                button.disabled = false;
            }
        });
    });
});