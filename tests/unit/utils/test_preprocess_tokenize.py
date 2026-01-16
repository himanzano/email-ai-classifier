import pytest
from app.utils.preprocess import preprocess_text, tokenize_text


class TestTokenizeTextFunction:
    """
    Testes unitários para a função `tokenize_text` isoladamente.
    """

    @pytest.mark.parametrize(
        "input_text, expected_tokens",
        [
            # 1. Casos básicos
            ("Olá mundo, tudo bem?", ["Olá", "mundo", "tudo", "bem"]),
            ("Texto simples sem pontuação", ["Texto", "simples", "sem", "pontuação"]),
            
            # 2. Preservação de acentos e tokens especiais
            ("A taxa de juros é 15%.", ["A", "taxa", "de", "juros", "é", "15"]),
            ("O valor é R$ 100,00.", ["O", "valor", "é", "R", "100,00"]),
            ("Processando tokens como <NUM> e <NUM>%.", ["Processando", "tokens", "como", "<NUM>", "e", "<NUM>%"]),
            
            # 3. Casos de borda
            ("", []),
            ("   ", []),
            ("  \n \t  ", []),
            ("apenas.pontuação!", ["apenas", "pontuação"]),
            ("palavras-hifenizadas", ["palavras", "hifenizadas"]),
            ("multiplos   espaços", ["multiplos", "espaços"]),
            ("texto\ncom\nquebra de linha", ["texto", "com", "quebra", "de", "linha"]),
        ]
    )
    def test_tokenize_scenarios(self, input_text, expected_tokens):
        """Testa a tokenização em vários cenários."""
        assert tokenize_text(input_text) == expected_tokens


class TestTokenizationInPipeline:
    """
    Testes de integração da tokenização com o pipeline `preprocess_text`.
    """

    def test_returns_string_when_tokenize_is_false(self):
        """Garante que o retorno é uma string quando a tokenização está desativada."""
        result = preprocess_text("Um texto de exemplo.", tokenize=False)
        assert isinstance(result, str)
        assert result == "um texto de exemplo."

    def test_returns_list_when_tokenize_is_true(self):
        """Garante que o retorno é uma lista de strings quando a tokenização está ativada."""
        result = preprocess_text("Um texto de exemplo.", tokenize=True)
        assert isinstance(result, list)
        assert all(isinstance(token, str) for token in result)
        assert result == ["um", "texto", "de", "exemplo"]

    def test_tokenization_is_the_last_step(self):
        """
        Valida se a tokenização ocorre após todas as outras etapas de pré-processamento.
        """
        input_text = "  O VALOR de R$ 1.234,56 foi APROVADO para estas casas."
        
        # Execução do pipeline completo com tokenização
        tokenized_result = preprocess_text(
            input_text,
            remove_stopwords=True,
            lemmatize=True,
            normalize_numbers=True,
            tokenize=True
        )

        # Resultado esperado após todas as etapas (antes da tokenização)
        # 1. Lowercase + Whitespace: "o valor de r$ 1.234,56 foi aprovado para estas casas."
        # 2. Normalize Numbers: "o valor de r$ <NUM> foi aprovado para estas casas."
        # 3. Remove Stopwords: "valor r$ <NUM> aprovado casas."
        # 4. Lemmatize: "valor r$ <NUM> aprovado casa."
        # 5. Tokenize
        expected_tokens = ["valor", "r", "<NUM>", "aprovado", "casa"]

        assert tokenized_result == expected_tokens

    @pytest.mark.parametrize(
        "input_text, tokenize, expected_output",
        [
            ("Texto com <NUM>%.", False, "texto com <NUM>%."),
            ("Texto com <NUM>%.", True, ["texto", "com", "<NUM>%"]),
            ("  Muitos   espaços  ", True, ["muitos", "espaços"]),
            ("\nLinhas\ndiferentes\n", True, ["linhas", "diferentes"])
        ]
    )
    def test_pipeline_with_edge_cases(self, input_text, tokenize, expected_output):
        """
        Testa o comportamento do pipeline com tokenização em diferentes casos de borda.
        """
        result = preprocess_text(input_text, tokenize=tokenize)
        assert result == expected_output

    def test_pipeline_with_only_punctuation_and_tokenization(self):
        """Testa se um texto com apenas pontuação resulta em lista vazia com tokenização."""
        result = preprocess_text(".,;!?-...", tokenize=True)
        assert result == []
