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
            step.classList.toggle('active', stepNumber <= currentStep);
        });
    };

    const showLoading = (isLoading) => {
        form.style.display = isLoading ? 'none' : 'block';
        resultSection.classList.toggle('hidden', !isLoading);
        loadingState.style.display = isLoading ? 'flex' : 'none';
        
        if (isLoading) {
            successState.classList.add('hidden');
            errorState.classList.add('hidden');
            updateFlowIndicator(2);
        }
    };

    const showSuccess = (data) => {
        loadingState.style.display = 'none';
        successState.classList.remove('hidden');
        
        categoryBadge.textContent = data.category;
        categoryBadge.className = 'badge text-white'; // Reseta classes de cor
        if (data.category === 'Produtivo') {
            categoryBadge.classList.add('bg-status-productive');
        } else {
            categoryBadge.classList.add('bg-status-improductive');
        }

        responseTextEl.textContent = data.response;
        updateFlowIndicator(3);
    };

    const showError = (message) => {
        loadingState.style.display = 'none';
        resultSection.classList.remove('hidden');
        successState.classList.add('hidden');
        errorState.classList.remove('hidden');
        errorMessageEl.textContent = message || 'Não foi possível processar sua solicitação. Tente novamente.';
        updateFlowIndicator(1);
    };
    
    const resetUI = () => {
        form.reset();
        emailContentEl.value = '';
        fileUploadEl.value = ''; // Limpa a seleção do arquivo
        fileNameEl.textContent = '';
        resultSection.classList.add('hidden');
        loadingState.style.display = 'none';
        successState.classList.add('hidden');
        errorState.classList.add('hidden');
        form.style.display = 'block';
        updateFlowIndicator(1);
    };

    // --- Lógica de Eventos ---

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = fileUploadEl.files[0];
        const emailText = emailContentEl.value.trim();

        if (!emailText && !file) {
            showError("Por favor, cole o conteúdo do e-mail ou anexe um arquivo.");
            return;
        }

        showLoading(true);
        
        try {
            let response;
            if (file) {
                const formData = new FormData();
                formData.append('file', file);
                response = await fetch('/api/process-email', { 
                    method: 'POST', 
                    body: formData 
                });
            } else {
                response = await fetch('/api/process-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email_content: emailText }),
                });
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: `Erro no servidor: ${response.status}` }));
                throw new Error(errorData.detail);
            }

            const data = await response.json();
            showSuccess(data);

        } catch (error) {
            showError(`Falha na comunicação com a API: ${error.message}`);
        }
    });

    fileUploadEl.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameEl.textContent = `Arquivo: ${file.name}`;
            const reader = new FileReader();
            reader.onload = (event) => {
                emailContentEl.value = event.target.result;
            };
            reader.readAsText(file);
        }
    });

    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(responseTextEl.textContent).then(() => {
            const originalBtnContent = copyBtn.innerHTML;
            copyBtn.innerHTML = `<ion-icon name="checkmark-outline" class="text-green-500"></ion-icon> <span>Copiado!</span>`;
            setTimeout(() => { copyBtn.innerHTML = originalBtnContent; }, 2000);
        });
    });
    
    tryAgainBtn.addEventListener('click', resetUI);
    analyzeAnotherBtn.addEventListener('click', resetUI);

    resetUI();
});