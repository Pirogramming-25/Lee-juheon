let answer = [];
let attempts = 9;
let gameOver = false;

function generateAnswer() {
    const nums = [];
    while (nums.length < 3) {
        const n = Math.floor(Math.random() * 10);
        if (!nums.includes(n)) {
            nums.push(n);
        }
    }
    return nums;
}

function initGame() {
    attempts = 9;
    gameOver = false;
    answer = generateAnswer();

    document.getElementById("attempts").textContent = attempts;
    document.getElementById("results").textContent = "";
    document.getElementById("game-result-img").src = "";
    document.getElementById("number1").value = "";
    document.getElementById("number2").value = "";
    document.getElementById("number3").value = "";
    document.querySelector(".submit-button").disabled = false;
}

function check_numbers() {
    if (gameOver) return;

    const input1 = document.getElementById("number1");
    const input2 = document.getElementById("number2");
    const input3 = document.getElementById("number3");

    if (input1.value === "" || input2.value === "" || input3.value === "") {
        input1.value = "";
        input2.value = "";
        input3.value = "";
        return;
    }

    const guess = [Number(input1.value), Number(input2.value), Number(input3.value)];

    attempts -= 1;
    document.getElementById("attempts").textContent = attempts;

    let strike = 0;
    let ball = 0;

    for (let i = 0; i < 3; i++) {
        if (guess[i] === answer[i]) {
            strike++;
        } else if (answer.includes(guess[i])) {
            ball++;
        }
    }

    addResultRow(guess, strike, ball);

    input1.value = "";
    input2.value = "";
    input3.value = "";

    if (strike === 3) {
        endGame(true);
    } else if (attempts === 0) {
        endGame(false);
    }
}

function addResultRow(guess, strike, ball) {
    const result = document.getElementById("results");
    result.style.width = "100%";

    const row = document.createElement("div");
    row.className = "check-result";
    row.style.justifyContent = "space-between";
    row.style.width = "100%";

    const left = document.createElement("div");
    left.className = "left";
    left.textContent = guess.join(" ");

    const colon = document.createElement("div");
    colon.textContent = ":";

    const right = document.createElement('div');
    right.className = 'right';

    if (strike === 0 && ball === 0) {
        right.innerHTML = `<span class="out num-result">O</span>`;
    } else {
        right.innerHTML = `${strike} <span class="strike num-result">S</span> ${ball} <span class="ball num-result">B</span>`;
    }

    row.appendChild(left);
    row.appendChild(colon);
    row.appendChild(right);
    result.appendChild(row);
}

function endGame(success) {
    gameOver = true;
    document.querySelector(".submit-button").disabled = true;
    document.getElementById("game-result-img").src = success ? 'success.png' : 'fail.png';
}

window.addEventListener("DOMContentLoaded", initGame);