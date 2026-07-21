const inputEl = document.getElementById("summarize-input");
const runBtn = document.getElementById("summarize-run-btn");
const loadingEl = document.getElementById("summarize-loading");
const errorEl = document.getElementById("summarize-error");
const resultEl = document.getElementById("summarize-result");
const historyListEl = document.getElementById("summarize-history-list");

runBtn.addEventListener("click", async () => {
    const text = inputEl.value;

    errorEl.style.display = "none";
    resultEl.style.display = "none";

    runBtn.disabled = true;
    inputEl.disabled = true;
    loadingEl.style.display = "block";

    try {
        const response = await fetch("/summarize/run/", {
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

    const p1 = document.createElement("p");
    p1.textContent = `원문 길이: ${result.original_length}자`;
    resultEl.appendChild(p1);

    const p2 = document.createElement("p");
    p2.textContent = `요약문 길이: ${result.summary_length}자`;
    resultEl.appendChild(p2);

    const p3 = document.createElement("p");
    p3.textContent = `요약 비율: ${result.summary_ratio}%`;
    resultEl.appendChild(p3);

    const label = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = "요약 결과:";
    label.appendChild(strong);
    resultEl.appendChild(label);

    const summaryP = document.createElement("p");
    summaryP.textContent = result.summary;
    resultEl.appendChild(summaryP);

    resultEl.style.display = "block";
}

function prependHistoryItem(text, result) {
    const emptyItem = historyListEl.querySelector(".empty-history");
    if (emptyItem) {
        emptyItem.remove();
    }

    const li = document.createElement("li");
    li.textContent = `${text.slice(0, 50)} → ${result.summary.slice(0, 50)} (방금 실행)`;
    historyListEl.insertBefore(li, historyListEl.firstChild);

    while (historyListEl.children.length > 5) {
        historyListEl.removeChild(historyListEl.lastChild);
    }
}