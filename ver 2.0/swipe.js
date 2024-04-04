document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.container');
    const prevBtns = document.querySelectorAll('.prev');
    const nextBtns = document.querySelectorAll('.next');
    const cards = document.querySelectorAll('.award_card');
    let currentIndex = 0;
    const cardWidth = cards[0].offsetWidth; // 첫 번째 카드의 너비

    // 초기에 첫 번째 카드만 보이도록 설정하고, 첫 번째 카드의 클래스를 "current"로 설정합니다.
    cards.forEach((card, index) => {
        if (index === currentIndex) {
            card.classList.add('current');
        }
        card.style.marginRight = index === cards.length - 1 ? '0' : `${-cardWidth}px`; // 첫 번째 카드만 왼쪽으로 이동하도록 설정
    });

    // 이전 버튼 클릭 이벤트 설정
    prevBtns.forEach(prevBtn => {
        prevBtn.addEventListener('click', function() {
            if (currentIndex > 0) {
                cards[currentIndex].classList.remove('current'); // 이전 카드의 클래스를 제거합니다.
                currentIndex--;
                cards[currentIndex].classList.add('current'); // 현재 카드의 클래스를 추가합니다.
                cards.forEach((card, index) => {
                    card.style.marginRight = index === currentIndex ? '0' : `${-cardWidth}px`;
                });
                updateArrowOpacity(); // 화살표의 투명도를 업데이트합니다.
            }
        });
    });

    // 다음 버튼 클릭 이벤트 설정
    nextBtns.forEach(nextBtn => {
        nextBtn.addEventListener('click', function() {
            if (currentIndex < cards.length - 1) {
                cards[currentIndex].classList.remove('current'); // 현재 카드의 클래스를 제거합니다.
                currentIndex++;
                cards[currentIndex].classList.add('current'); // 다음 카드의 클래스를 추가합니다.
                cards.forEach((card, index) => {
                    card.style.marginRight = index === currentIndex ? '0' : `${-cardWidth}px`;
                });
                updateArrowOpacity(); // 화살표의 투명도를 업데이트합니다.
            }
        });
    });

    // 화살표의 투명도를 업데이트하는 함수
    function updateArrowOpacity() {
        prevBtns.forEach(prevBtn => {
            prevBtn.style.opacity = currentIndex === 0 ? '0.5' : '1'; // 첫 번째 카드일 때 이전 버튼의 투명도를 조절합니다.
        });
        nextBtns.forEach(nextBtn => {
            nextBtn.style.opacity = currentIndex === cards.length - 1 ? '0.5' : '1'; // 마지막 카드일 때 다음 버튼의 투명도를 조절합니다.
        });
    }

    // 초기에 화살표의 투명도를 설정합니다.
    updateArrowOpacity();
});

