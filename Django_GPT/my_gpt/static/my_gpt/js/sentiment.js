const inputEl = document.getElementById("sentiment-input");
const runBtn = document.getElementById("sentiment-run-btn");
const loadingEl = document.getElementById("sentiment-loading");
const errorEl = document.getElementById("sentiment-error");
const resultEl = document.getElementById("sentiment-result");
const historyListEl = document.getElementById("sentiment-history-list");

// 비로그인 사용자용 임시 기록 (새로고침 시 초기화됨)
let localHistory = [];

runBtn.addEventListener("click", async () => {
    const text = inputEl.value;

    errorEl.style.display = "none";
    resultEl.style.display = "none";

    runBtn.disabled = true;
    inputEl.disabled = true;
    loadingEl.style.display = "block";

    try {
        const response = await fetch("/sentiment/run/", {
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

        if (!window.IS_AUTHENTICATED) {
            addLocalHistory(text, result);
        } else {
            // 로그인 상태면 새로고침 없이 최근 기록 목록에 즉시 추가
            prependHistoryItem(text, result);
        }
    } catch (err) {
        errorEl.textContent = "네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
        errorEl.style.display = "block";
    } finally {
        runBtn.disabled = false;
        inputEl.disabled = false;
        loadingEl.style.display = "none";
    }
});

function scoreClass(label) {
    const l = label.toLowerCase();
    if (l.includes("positive")) return "positive";
    if (l.includes("negative")) return "negative";
    return "neutral";
}

function renderResult(result) {
    resultEl.innerHTML = "";

    const labelP = document.createElement("p");
    labelP.append("감정: ");
    const labelStrong = document.createElement("strong");
    labelStrong.textContent = result.label;
    labelP.appendChild(labelStrong);
    resultEl.appendChild(labelP);

    const scoreP = document.createElement("p");
    scoreP.textContent = `신뢰도: ${result.score}%`;
    resultEl.appendChild(scoreP);

    result.all_scores.forEach((item) => {
        const meter = document.createElement("div");
        meter.className = "meter";

        const labelSpan = document.createElement("span");
        labelSpan.className = "meter-label";
        labelSpan.textContent = item.label;
        meter.appendChild(labelSpan);

        const track = document.createElement("div");
        track.className = "meter-track";
        const fill = document.createElement("div");
        fill.className = `meter-fill ${scoreClass(item.label)}`;
        fill.style.width = `${item.score}%`;
        track.appendChild(fill);
        meter.appendChild(track);

        const valueSpan = document.createElement("span");
        valueSpan.className = "meter-value";
        valueSpan.textContent = `${item.score}%`;
        meter.appendChild(valueSpan);

        resultEl.appendChild(meter);
    });

    resultEl.style.display = "block";
}

function addLocalHistory(text, result) {
    localHistory.unshift({ text, result });
    if (localHistory.length > 5) {
        localHistory.pop();
    }

    historyListEl.innerHTML = "";
    localHistory.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.text.slice(0, 50)} → ${item.result.label}`;
        historyListEl.appendChild(li);
    });
}

function prependHistoryItem(text, result) {
    const emptyItem = historyListEl.querySelector(".empty-history");
    if (emptyItem) {
        emptyItem.remove();
    }

    const li = document.createElement("li");
    li.textContent = `${text.slice(0, 50)} → ${result.label} (방금 실행)`;
    historyListEl.insertBefore(li, historyListEl.firstChild);

    while (historyListEl.children.length > 5) {
        historyListEl.removeChild(historyListEl.lastChild);
    }
}