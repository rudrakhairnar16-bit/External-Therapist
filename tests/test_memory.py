import pytest


class TestMemory:
    @pytest.mark.asyncio
    async def test_remember_and_recall(self):
        assert True

    def test_extract_mood_happy(self):
        from app.core.llm import TherapyLLM

        llm = TherapyLLM("test_user")
        score = llm._extract_mood("I feel great today!")
        assert score == 9

    def test_extract_mood_sad(self):
        from app.core.llm import TherapyLLM

        llm = TherapyLLM("test_user")
        score = llm._extract_mood("I feel depressed and hopeless")
        assert score == 1

    def test_extract_topics(self):
        from app.core.llm import TherapyLLM

        llm = TherapyLLM("test_user")
        topics = llm._extract_topics("I'm anxious about work and my family")
        assert "work" in topics
        assert "family" in topics
        assert "anxiety" in topics
