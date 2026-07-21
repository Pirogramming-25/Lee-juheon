const inputEl = document.getElementById("moderate-input");
const runBtn = document.getElementById("moderate-run-btn");
const loadingEl = document.getElementById("moderate-loading");
const errorEl = document.getElementById("moderate-error");
const resultEl = document.getElementById("moderate-result");
const historyListEl = document.getElementById("moderate-history-list");

runBtn.addEventListener("click", async () => {
    const text = inputEl.value;

    errorEl.style.display = "none";
    resultEl.style.display = "none";

    runBtn.disabled = true;
    inputEl.disabled = true;
    loadingEl.style.display = "block";

    try {
        const response = await fetch("/moderate/run/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN,
            },
            body: JSON.stringify({ text: text }),
        });

        const data = await response.json();

        if (!response.ok) {
            errorEl.textContent = data.error || "오류가 발생했습니다.";
            errorEl.style.display = "block";
            return;
        }

        const result = data.data;
        renderResult(result);
        prependHistoryItem(text, result);
    } catch (err) {
        errorEl.textContent = "네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
        errorEl.style.display = "block";
    } finally {
        runBtn.disabled = false;
        inputEl.disabled = false;
        loadingEl.style.display = "none";
    }
});

function renderResult(result) {
    resultEl.innerHTML = "";

    const labelP = document.createElement("p");
    labelP.append("최고 위험 레이블: ");
    const strong = document.createElement("strong");
    strong.textContent = result.highest_label;
    labelP.appendChild(strong);
    resultEl.appendChild(labelP);

    const scoreP = document.createElement("p");
    scoreP.textContent = `위험 점수: ${result.highest_score}%`;
    resultEl.appendChild(scoreP);

    const ul = document.createElement("ul");
    result.all_scores.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.label}: ${item.score}%`;
        ul.appendChild(li);
    });
    resultEl.appendChild(ul);

    resultEl.style.display = "block";
}

function prependHistoryItem(text, result) {
    const emptyItem = historyListEl.querySelector(".empty-history");
    if (emptyItem) {
        emptyItem.remove();
    }

    const li = document.createElement("li");
    li.textContent = `${text.slice(0, 50)} → ${result.highest_label} (방금 실행)`;
    historyListEl.insertBefore(li, historyListEl.firstChild);

    while (historyListEl.children.length > 5) {
        historyListEl.removeChild(historyListEl.lastChild);
    }
}