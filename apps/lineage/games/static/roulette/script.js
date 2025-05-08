document.addEventListener("DOMContentLoaded", () => {
    const spinBtn = document.getElementById("spinBtn");
    const resultDisplay = document.getElementById("result");
    const rouletteList = document.getElementById("rouletteList");
  
    // Renderiza os prêmios
    prizes.forEach(prize => {
      const li = document.createElement("li");
      li.innerHTML = `<img src="${prize.image_url}" alt="${prize.name}" /> ${prize.name}`;
      rouletteList.appendChild(li);
    });
  
    spinBtn.addEventListener("click", () => {
      spinBtn.disabled = true;
      resultDisplay.textContent = "Girando...";
  
      fetch(SPIN_URL, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          if (data.error) {
            resultDisplay.textContent = data.error;
            spinBtn.disabled = false;
            return;
          }
  
          const index = prizes.findIndex(p => p.id === data.id);
          const itemHeight = 100;
          const spinRounds = 5;
          const offset = (itemHeight * index) + (itemHeight / 2);
  
          rouletteList.style.transition = 'none';
          rouletteList.style.transform = `translateY(0px)`;
  
          requestAnimationFrame(() => {
            rouletteList.style.transition = 'transform 3s ease-out';
            const totalMove = (prizes.length * itemHeight * spinRounds) + offset;
            rouletteList.style.transform = `translateY(-${totalMove}px)`;
          });
  
          setTimeout(() => {
            resultDisplay.textContent = `Você ganhou: ${data.name}!`;
            spinBtn.disabled = false;
          }, 3200);
        })
        .catch(err => {
          resultDisplay.textContent = "Erro ao girar a roleta.";
          spinBtn.disabled = false;
          console.error(err);
        });
    });
  });
  