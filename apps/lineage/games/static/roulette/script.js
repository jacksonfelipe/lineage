function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {
    const spinBtn = document.getElementById("spinBtn");
    const resultDisplay = document.getElementById("result");
    const rouletteList = document.getElementById("rouletteList");
    const body = document.body;

    // Renderiza os prêmios duplicados para permitir várias voltas
    const repeat = 10; // número de repetições da lista
    prizes.forEach(() => {
        for (let i = 0; i < repeat; i++) {
            prizes.forEach(prize => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <img src="${prize.image_url}" alt="${prize.name}" />
                    ${prize.name}: +${prize.enchant} - ${prize.rarity}
                `;
                rouletteList.appendChild(li);
            });
        }
    });

    // Função para adicionar o efeito de partículas na tela (fogos de artifício)
    function showParticles() {
        const particleCount = 20; // Número de partículas (ajuste conforme necessário)
        for (let i = 0; i < particleCount; i++) {
            const particles = document.createElement('div');
            particles.classList.add('particles');
            body.appendChild(particles);

            // Definindo as direções aleatórias para dispersão
            const angle = Math.random() * 360; // Ângulo aleatório para dispersão
            const distance = Math.random() * 150 + 100; // Distância aleatória para espalhar as partículas
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;

            // Aplica a transformação aleatória
            particles.style.setProperty('--x', `${x}px`);
            particles.style.setProperty('--y', `${y}px`);

            // Remove a animação após o término
            setTimeout(() => {
                body.removeChild(particles);
            }, 1500);
        }
    }

    // Função para criar partículas aleatórias
    function createParticles() {
        const body = document.querySelector('.roulette-wrapper');
        const particleCount = 20;
        
        for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        body.appendChild(particle);

        // Efeito de dispersão aleatória
        const angle = Math.random() * 360;
        const distance = Math.random() * 150 + 100;
        const x = Math.cos(angle) * distance;
        const y = Math.sin(angle) * distance;

        // Aplicando os estilos para dispersão
        particle.style.setProperty('--x', `${x}px`);
        particle.style.setProperty('--y', `${y}px`);

        // Remover partículas após o efeito
        setTimeout(() => {
            body.removeChild(particle);
        }, 1500);
        }
    }

    // Função para exibir partículas de fogos de artifício
    function showFireworks() {
        const fireworks = document.createElement('div');
        fireworks.classList.add('fireworks');
        document.body.appendChild(fireworks);

        // Remover após animação
        setTimeout(() => {
        document.body.removeChild(fireworks);
        }, 2000);
    }

    spinBtn.addEventListener("click", () => {
        spinBtn.disabled = true;
        spinBtn.classList.remove("pulse");
        resultDisplay.textContent = "Girando...";

        fetch(SPIN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Aqui está o segredo
            },
            credentials: 'include',
            body: JSON.stringify({})  // Pode ser vazio ou incluir dados extras
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    resultDisplay.textContent = data.error;
                    spinBtn.disabled = false;
                    spinBtn.classList.add("pulse");
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
                    const totalItems = prizes.length * repeat;
                    const targetIndex = (prizes.length * (repeat - 1)) + index;
                    const totalMove = (itemHeight * targetIndex) + (itemHeight / 2);
                    rouletteList.style.transform = `translateY(-${totalMove}px)`;
                });

                setTimeout(() => {
                    resultDisplay.textContent = `Você ganhou: ${data.name}!`;
                    spinBtn.disabled = false;
                    spinBtn.classList.add("pulse");

                    // Adiciona o efeito de partículas se o prêmio for especial
                    if (data.rarity === "LENDARIO") {
                        showParticles();
                        createParticles();
                        showFireworks();
                    }

                    // Exibir o modal com informações do prêmio
                    document.getElementById("modalPrizeImg").src = data.image_url;
                    document.getElementById("modalPrizeName").textContent = data.name;
                    document.getElementById("modalPrizeRarity").textContent = `Raridade: ${data.rarity}`;
                    // Mensagem personalizada dependendo da raridade
                    const msg = data.rarity === "LENDARIO"
                    ? `🔥 Parabéns, você ganhou um prêmio Lendário: ${data.name}!`
                    : `Você ganhou: ${data.name}! Aproveite sua recompensa.`;

                    document.getElementById("modalPrizeMsg").textContent = msg;
                    const modal = new bootstrap.Modal(document.getElementById('rewardModal'));
                    modal.show();

                    // Reset visual após girar
                    rouletteList.style.transition = 'none';
                    rouletteList.style.transform = `translateY(0px)`;
                    rouletteList.innerHTML = '';
                    for (let i = 0; i < repeat; i++) {
                        prizes.forEach(prize => {
                            const li = document.createElement("li");
                            li.innerHTML = `
                                <img src="${prize.image_url}" alt="${prize.name}" />
                                ${prize.name} - ${prize.item_name} (Enchant: ${prize.enchant}, Raridade: ${prize.rarity})
                            `;
                            rouletteList.appendChild(li);
                        });
                    }
                }, 3200);
            })
            .catch(err => {
                resultDisplay.textContent = "Erro ao girar a roleta.";
                spinBtn.disabled = false;
                spinBtn.classList.add("pulse");
                console.error(err);
            });
    });
});
