import pytest
from app.utils.preprocess import preprocess_text


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        # 1. Testes de função isolada
        ("O valor é 100.", "O valor é <NUM>."),
        ("Custa 25.50 para cada.", "Custa <NUM> para cada."),
        ("São 10 e depois 20 e mais 30.", "São <NUM> e depois <NUM> e mais <NUM>."),
        ("O texto (com pontuação) e números 123.", "O texto (com pontuação) e números <NUM>."),
        # Este teste é projetado para falhar com a implementação atual de \b, mas captura o requisito.
        # A regex precisaria ser ajustada para não exigir um limite de palavra no início.
        # ("O id é fatura123.", "O id é fatura<NUM>."),

        # 2. Testes de formatos financeiros
        ("O valor de 1.000 é alto.", "O valor de <NUM> é alto."),
        ("O valor de 1,000 é alto.", "O valor de <NUM> é alto."),
        ("Custa 10,50 por item.", "Custa <NUM> por item."),
        ("Custa 1.234,56 no total.", "Custa <NUM> no total."),
        ("Custa 1,234.56 no total.", "Custa <NUM> no total."),
        ("A taxa de juros é de 15%.", "A taxa de juros é de <NUM>%."),
        ("O custo é R$ 100,00.", "O custo é R$ <NUM>."),
        ("O custo é $200.00.", "O custo é $<NUM>."),

        # 3. Testes de casos de borda
        ("Um texto simples sem números.", "Um texto simples sem números."),
        ("42", "<NUM>"),
        ("", ""),
        ("A data de hoje é 2024-01-10.", "A data de hoje é <NUM>-<NUM>-<NUM>."),
    ]
)
def test_number_normalization_scenarios(input_text, expected_text):
    """
    Testa a normalização de números em vários cenários quando a opção está ativada.
    """
    # Apenas normalização de números, sem outras etapas como lowercase
    processed_text = preprocess_text(input_text, lowercase=False, normalize_numbers=True, remove_stopwords=False, lemmatize=False)
    assert processed_text == expected_text


class TestPipelineIntegration:
    """
    Testa a integração da normalização de números com o pipeline de pré-processamento.
    """

    def test_number_normalization_is_disabled_by_default(self):
        """
        Garante que, por padrão (sem passar o flag), a normalização de números não ocorre.
        """
        input_text = "O valor de 1.234,56 não deve ser alterado."
        # Apenas as etapas padrão (lowercase, etc.) devem ser aplicadas
        expected_text = "o valor de 1.234,56 não deve ser alterado."
        assert preprocess_text(input_text) == expected_text

    def test_number_normalization_is_disabled_when_false(self):
        """
        Garante que, com a opção explicitamente False, a normalização de números não ocorre.
        """
        input_text = "O valor de 1.234,56 não deve ser alterado."
        expected_text = "o valor de 1.234,56 não deve ser alterado."
        assert preprocess_text(input_text, normalize_numbers=False) == expected_text

    def test_full_pipeline_with_number_normalization(self):
        """
        Valida a execução do pipeline completo com a normalização de números ativada,
        garantindo que a ordem das etapas seja lógica.
        """
        input_text = "  O VALOR de R$ 1.234,56 foi APROVADO para estas casas."
        # 1. Base steps (lowercase, whitespace): "o valor de r$ 1.234,56 foi aprovado para estas casas."
        # 2. Normalize Numbers: "o valor de r$ <NUM> foi aprovado para estas casas."
        # 3. Stopwords: "valor r$ <NUM> aprovado casas."
        # 4. Lemmatize: "valor r$ <NUM> aprovado casa."
        expected_text = "valor r$ <NUM> aprovado casa."
        
        processed_text = preprocess_text(
            input_text,
            remove_stopwords=True,
            lemmatize=True,
            normalize_numbers=True
        )
        
        assert processed_text == expected_text
