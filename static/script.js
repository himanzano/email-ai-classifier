document.addEventListener('DOMContentLoaded', () => {
    // --- Seletores de Elementos do DOM ---
    const form = document.getElementById('email-form');
    const submitBtn = document.getElementById('submit-btn');
    const emailContentEl = document.getElementById('email-content');
    const fileUploadEl = document.getElementById('file-upload');
    const fileNameEl = document.getElementById('file-name');

    const resultSection = document.getElementById('result-section');
    const loadingState = document.getElementById('loading-state');
    const successState = document.getElementById('success-state');
    const errorState = document.getElementById('error-state');
    
    const categoryBadge = document.getElementById('category-badge');
    const responseTextEl = document.getElementById('response-text');
    const copyBtn = document.getElementById('copy-btn');
    const errorMessageEl = document.getElementById('error-message');

    const tryAgainBtn = document.getElementById('try-again-btn');
    const analyzeAnotherBtn = document.getElementById('analyze-another-btn');

    const steps = document.querySelectorAll('.step');

    // --- Funções de Controle de UI ---

    const updateFlowIndicator = (currentStep) => {
        steps.forEach(step => {
            const stepNumber = parseInt(step.dataset.step, 10);
            if (stepNumber <= currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    };

    const showLoading = (isLoading) => {
        if (isLoading) {
            resultSection.classList.remove('hidden');
            loadingState.classList.remove('hidden');
            successState.classList.add('hidden');
            errorState.classList.add('hidden');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Analisando...';
            updateFlowIndicator(2);
        } else {
            loadingState.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analisar e Gerar Resposta';
        }
    };

    const showSuccess = (data) => {
        successState.classList.remove('hidden');
        
        categoryBadge.textContent = data.category;
        if (data.category === 'Produtivo') {
            categoryBadge.className = 'badge bg-status-productive text-white';
        } else {
            categoryBadge.className = 'badge bg-status-improductive text-white';
        }

        responseTextEl.textContent = data.response;
        updateFlowIndicator(3);
    };

    const showError = (message) => {
        errorState.classList.remove('hidden');
        errorMessageEl.textContent = message || 'Não foi possível processar sua solicitação. Tente novamente.';
        updateFlowIndicator(1); // Volta para a primeira etapa
    };
    
    const resetUI = () => {
        form.reset();
        fileNameEl.textContent = '';
        resultSection.classList.add('hidden');
        loadingState.classList.add('hidden');
        successState.classList.add('hidden');
        errorState.classList.add('hidden');
        updateFlowIndicator(1);
    };

    // --- Lógica de Eventos ---

    // Envio do formulário
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const emailText = emailContentEl.value.trim();

        if (!emailText) {
            showError("O campo de conteúdo do e-mail não pode estar vazio.");
            resultSection.classList.remove('hidden'); // Mostra a seção de erro
            return;
        }

        showLoading(true);

        try {
            // Simulação de chamada de API. Substitua pelo seu endpoint real.
            // Ex: const response = await fetch('/api/classify', { ... });
            const response = await fetch('/api/process-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email_content: emailText }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(errorData?.detail || `Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            showSuccess(data);

        } catch (error) {
            showError(error.message);
        } finally {
            showLoading(false);
        }
    });

    // Upload de arquivo
    fileUploadEl.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameEl.textContent = `Arquivo selecionado: ${file.name}`;
            const reader = new FileReader();
            reader.onload = (event) => {
                emailContentEl.value = event.target.result;
            };
            reader.readAsText(file);
        }
    });

    // Botão de Copiar
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(responseTextEl.textContent).then(() => {
            const originalBtnContent = copyBtn.innerHTML;
            copyBtn.innerHTML = `
                <ion-icon name="checkmark-outline"></ion-icon>
                <span>Copiado!</span>
            `;
            setTimeout(() => {
                copyBtn.innerHTML = originalBtnContent;
            }, 2000);
        });
    });
    
    // Botões para resetar a UI
    tryAgainBtn.addEventListener('click', resetUI);
    analyzeAnotherBtn.addEventListener('click', resetUI);

    // Estado inicial
    updateFlowIndicator(1);
});
