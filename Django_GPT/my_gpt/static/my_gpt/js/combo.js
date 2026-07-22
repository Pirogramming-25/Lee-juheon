const inputEl = document.getElementById("combo-input");
const runBtn = document.getElementById("combo-run-btn");
const regenerateBtn = document.getElementById("combo-regenerate-btn");
const loadingEl = document.getElementById("combo-loading");
const errorEl = document.getElementById("combo-error");
const resultEl = document.getElementById("combo-result");
const historyListEl = document.getElementById("combo-history-list");

// 재생성 버튼을 위해 마지막으로 실행한 원문을 기억해둠
let lastOriginalText = "";

runBtn.addEventListener("click", () => {
    runCombo(inputEl.value, false);
});

regenerateBtn.addEventListener("click", () => {
    runCombo(lastOriginalText, true);
});

async function runCombo(text, regenerate) {
    errorEl.style.display = "none";

    if (!regenerate) {
        resultEl.style.display = "none";
    }

    setBusy(true);

    try {
        const response = await fetch("/combo/run/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN,
            },
            body: JSON.stringify({
                text: text,
                regenerate: regenerate,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            errorEl.textContent = data.error || "오류가 발생했습니다.";
            errorEl.style.display = "block";
            return;
        }

        lastOriginalText = data.original_text;
        renderResult(data.original_text, data.data);
        prependHistoryItem(data.original_text, data.data);

        regenerateBtn.style.display = "inline-block";
    } catch (err) {
        errorEl.textContent = "네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.";
        errorEl.style.display = "block";
    } finally {
        setBusy(false);
    }
}

function setBusy(isBusy) {
    runBtn.disabled = isBusy;
    regenerateBtn.disabled = isBusy;
    inputEl.disabled = isBusy;
    loadingEl.style.display = isBusy ? "block" : "none";
}

function scoreClass(label) {
    const l = label.toLowerCase();
    if (l.includes("positive")) return "positive";
    if (l.includes("negative")) return "negative";
    return "neutral";
}

function buildMeter(label, score, cls) {
    const meter = document.createElement("div");
    meter.className = "meter";

    const labelSpan = document.createElement("span");
    labelSpan.className = "meter-label";
    labelSpan.textContent = label;
    meter.appendChild(labelSpan);

    const track = document.createElement("div");
    track.className = "meter-track";
    const fill = document.createElement("div");
    fill.className = `meter-fill ${cls}`;
    fill.style.width = `${score}%`;
    track.appendChild(fill);
    meter.appendChild(track);

    const valueSpan = document.createElement("span");
    valueSpan.className = "meter-value";
    valueSpan.textContent = `${score}%`;
    meter.appendChild(valueSpan);

    return meter;
}

function renderResult(originalText, result) {
    resultEl.innerHTML = "";

    function addSection(titleText, bodyEl) {
        const titleP = document.createElement("p");
        const strong = document.createElement("strong");
        strong.textContent = titleText;
        titleP.appendChild(strong);
        resultEl.appendChild(titleP);
        resultEl.appendChild(bodyEl);
    }

    const originalP = document.createElement("p");
    originalP.textContent = originalText;
    addSection("1. 입력 원문", originalP);

    const summaryP = document.createElement("p");
    summaryP.textContent = result.summary;
    addSection("2. 요약문", summaryP);

    const sentimentWrapper = document.createElement("div");
    sentimentWrapper.appendChild(
        buildMeter(result.sentiment.label, result.sentiment.score, scoreClass(result.sentiment.label))
    );
    addSection("3. 감정 분석", sentimentWrapper);

    const toxicityWrapper = document.createElement("div");
    const toxicitySummaryP = document.createElement("p");
    toxicitySummaryP.textContent = `최고 위험 레이블: ${result.toxicity.highest_label} (${result.toxicity.highest_score}%)`;
    toxicityWrapper.appendChild(toxicitySummaryP);

    result.toxicity.all_scores.forEach((item) => {
        toxicityWrapper.appendChild(buildMeter(item.label, item.score, "negative"));
    });
    addSection("4. 유해 표현 분석", toxicityWrapper);

    const verdictP = document.createElement("p");
    verdictP.textContent = result.verdict;
    addSection("5. 종합 판정", verdictP);

    resultEl.style.display = "block";
}

function prependHistoryItem(originalText, result) {
    const emptyItem = historyListEl.querySelector(".empty-history");
    if (emptyItem) {
        emptyItem.remove();
    }

    const li = document.createElement("li");
    li.textContent = `${originalText.slice(0, 50)} → ${result.summary.slice(0, 50)} (방금 실행)`;
    historyListEl.insertBefore(li, historyListEl.firstChild);

    while (historyListEl.children.length > 5) {
        historyListEl.removeChild(historyListEl.lastChild);
    }
}