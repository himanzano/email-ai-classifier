# Configuração do Google Cloud Platform (Vertex AI) para Desenvolvimento Local

Este guia detalha o processo de configuração de uma **Service Account** (Conta de Serviço) no Google Cloud Platform (GCP) para autenticar a aplicação localmente e permitir o acesso à API do Vertex AI (Gemini).

> **Nota de Segurança:** Nunca comite suas chaves JSON no Git. O arquivo `.gitignore` deste projeto já está configurado para ignorar arquivos terminados em `.json` na raiz e pastas de credenciais, mas sempre verifique.

---

## 1. Configuração no Console do Google Cloud

### Passo 1: Criar ou Selecionar um Projeto
1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/).
2. Crie um novo projeto ou selecione um existente.
3. Anote o **ID do Projeto** (Project ID), você precisará dele no arquivo `.env`.

### Passo 2: Habilitar a API Vertex AI
1. No menu de navegação, vá para **"APIs e Serviços" > "Biblioteca"**.
2. Pesquise por **"Vertex AI API"**.
3. Clique em **"Ativar"** (Enable).

### Passo 3: Criar uma Service Account (Conta de Serviço)
1. No menu de navegação, vá para **"IAM e Admin" > "Contas de serviço"**.
2. Clique em **"+ CRIAR CONTA DE SERVIÇO"**.
3. Preencha os detalhes:
    - **Nome da conta de serviço:** ex: `email-classifier-local-dev`
    - **ID da conta de serviço:** (gerado automaticamente)
    - **Descrição:** ex: "Conta para desenvolvimento local do classificador de emails"
4. Clique em **"CRIAR E CONTINUAR"**.

### Passo 4: Conceder Permissões (IAM)
Na etapa "Conceder a essa conta de serviço acesso ao projeto":
1. No filtro de papéis, pesquise por **"Vertex AI User"** (Usuário da Vertex AI).
2. Selecione o papel.
    - *Isso permite que a aplicação faça chamadas aos modelos (Gemini), mas não dá permissões administrativas excessivas.*
3. Clique em **"CONTINUAR"** e depois em **"CONCLUÍDO"**.

### Passo 5: Gerar a Chave JSON
1. Na lista de contas de serviço, clique no e-mail da conta que você acabou de criar.
2. Vá para a aba **"CHAVES"**.
3. Clique em **"ADICIONAR CHAVE" > "Criar nova chave"**.
4. Selecione o tipo **JSON**.
5. Clique em **"CRIAR"**.
6. O download do arquivo `.json` começará automaticamente. **Guarde este arquivo com segurança.**

---

## 2. Configuração Local

### Passo 1: Posicionar a Chave
1. Mova o arquivo JSON baixado para a raiz do projeto (ou um diretório seguro fora dele).
2. Renomeie o arquivo para algo simples, como `gcp-credentials.json` (opcional, mas facilita).

**Importante:** Certifique-se de que este arquivo NÃO será enviado para o GitHub. Verifique seu `.gitignore`.

### Passo 2: Configurar Variáveis de Ambiente (.env)

1. Se ainda não o fez, duplique o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Abra o arquivo `.env` e preencha as variáveis com os dados obtidos:

   ```ini
   # ID do seu projeto no GCP (Passo 1.3)
   GCP_PROJECT_ID="seu-project-id-aqui"

   # Região do GCP (recomendado: us-central1 para acesso aos modelos mais recentes)
   GCP_LOCATION="us-central1"

   # Caminho ABSOLUTO ou RELATIVO para o arquivo JSON da sua Service Account
   GOOGLE_APPLICATION_CREDENTIALS="gcp-credentials.json"
   ```

   *Nota: Se o arquivo JSON estiver na raiz do projeto, apenas o nome do arquivo basta.*

---

## 3. Testando a Configuração

Para verificar se a autenticação está funcionando:

1. Inicie a aplicação:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
2. Tente classificar um e-mail simples na interface.
3. Se a autenticação falhar, você verá erros relacionados a "PermissionDenied" ou "DefaultCredentialsError" no console.

---

## Resolução de Problemas Comuns

*   **Erro "Quota exceeded":** Verifique se você tem cota disponível para a Vertex AI API no seu projeto (novas contas podem ter limites baixos).
*   **Erro "API not enabled":** Aguarde alguns minutos após ativar a API Vertex AI.
*   **Permissão Negada:** Verifique se a Service Account tem o papel **"Vertex AI User"** corretamente atribuído.
