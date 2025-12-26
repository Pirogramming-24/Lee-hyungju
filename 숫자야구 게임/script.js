const game = {
    curAttempt: 0,
    maxAttempt: 10,
    answer: ""
}

const inputFieldList = document.querySelectorAll(".input-field");
const gameResultImg = document.getElementById("game-result-img");
const leftAttemptsSpan = document.getElementById("attempts");
const checkResultDiv = document.querySelector(".check-result");

let resultCnt = 1;

function updateUI() {
    leftAttemptsSpan.textContent = String(game.maxAttempt - game.curAttempt);
}
//초기화 함수
function initialize(){
    updateUI()
    //정답 생성 로직
    const digits = [];

    while (digits.length < 3) {
        const n = Math.floor(Math.random() * 10);
        if (!digits.includes(n)) digits.push(n);
    }

    game.answer = digits.join('');

    //CSS 고치는 로직 -> #results에 justify-content 추가 
    // resultsDiv.style.display = "flex"
    // resultsDiv.style.flexFlow = "row"
    // resultsDiv.style.justifyContent = "space-between"
}
//새 결과 열을 만드는 함수
function resultRowFactory(isOUT){
    const row = document.createElement('div');
    row.className = 'check-result';

    const left = document.createElement('div');
    left.className = 'left';

    const colon = document.createElement('span');
    colon.textContent = ':';

    const right = document.createElement('div');
    right.className = 'right';

    if(isOUT){
        const oLabel = document.createElement('span')
        oLabel.className = 'out num-result'
        oLabel.textContent = 'O'
        right.append(oLabel);
        row.append(left, colon, right);

        return { row, left };
    }
    const sNum = document.createElement('span');
    const sLabel = document.createElement('span');
    sLabel.className = 'strike num-result';
    sLabel.textContent = 'S';

    const bNum = document.createElement('span');
    const bLabel = document.createElement('span');
    bLabel.className = 'ball num-result';
    bLabel.textContent = 'B';

    right.append(sNum, sLabel, bNum, bLabel);
    row.append(left, colon, right);

    // row.textContent = "";
    return { row, left, sNum, bNum };
}
initialize();

function check_numbers(){
    //판단 로직
    let strike=0; 
    let ball=0;
    const guess = Array.from(inputFieldList)
                            .map(input => input.value)
                            .join(' ')
    
    inputFieldList.forEach((el,idx) => {
        if(el.value === game.answer[idx]) strike+=1;
        else if(game.answer.includes(el.value)) ball++;
    });
    

    //확인 결과 출력 
    //형식: 적은 숫자 : {strike}S {ball}B 
    //색깔 주의
    appendResult(strike,ball,guess);

    // 횟수 추가
    game.curAttempt++;
    //입력창 초기화
    inputFieldList.forEach((el) => {
        el.value = ""
    })

    if(strike === 3){
        //success 사진 띄우기
        gameResultImg.src = "success.png"
    }
    if(game.maxAttempt - game.curAttempt === 0){
        gameResultImg.src = "fail.png"
    }
    
    updateUI()
}

function appendResult(strike, ball, guessStr){
    const parent = checkResultDiv.parentNode;
    if(strike===0 && ball===0){
        const { row, left } = resultRowFactory(true);
        left.textContent = guessStr;
        parent.appendChild(row)
    } else {
        const r = resultRowFactory(false);
        r.left.textContent = guessStr;
        r.sNum.textContent = strike;
        r.bNum.textContent = ball;

        parent.appendChild(r.row)
    }
}
