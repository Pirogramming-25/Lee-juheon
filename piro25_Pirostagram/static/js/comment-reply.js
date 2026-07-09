document.addEventListener("DOMContentLoaded", () => {
    const replyToggleButtons = document.querySelectorAll(
        ".js-reply-toggle"
    );

    replyToggleButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const commentId = button.dataset.commentId;

            const replyForm = document.querySelector(
                `#reply-form-${commentId}`
            );

            if (!replyForm) {
                return;
            }

            const isHidden = replyForm.hidden;

            replyForm.hidden = !isHidden;

            if (isHidden) {
                const input = replyForm.querySelector(
                    "input[type=text]"
                );

                if (input) {
                    input.focus();
                }
            }
        });
    });
});
