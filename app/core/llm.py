from groq import AsyncGroq

from app.core import config as cfg
from app.core.memory import EternalMemory

_async_client = AsyncGroq(api_key=cfg.GROQ_API_KEY)


class TherapyLLM:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory = EternalMemory(user_id)

    async def respond(self, user_message: str) -> str:
        context = await self.memory.recall_formatted(user_message)

        system_prompt = (
            "You are a warm, empathetic therapist. You have access to the user's "
            "complete therapy history below. Reference past discussions naturally "
            "and show that you remember their journey. Be supportive, insightful, "
            "and gently guide them toward reflection and growth.\n\n"
            f"RELEVANT HISTORY FROM PAST SESSIONS:\n{context}"
        )

        response = await _async_client.chat.completions.create(
            model=cfg.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        reply = response.choices[0].message.content

        await self.memory.store_session(
            transcript=f"User: {user_message}\nTherapist: {reply}",
            mood_score=self._extract_mood(user_message),
            topics=self._extract_topics(user_message),
        )

        return reply

    def _extract_mood(self, text: str) -> int:
        keywords = {
            "depressed": 1,
            "sad": 2,
            "anxious": 3,
            "worried": 3,
            "stressed": 3,
            "okay": 5,
            "fine": 5,
            "good": 7,
            "happy": 8,
            "great": 9,
            "amazing": 10,
        }
        lower = text.lower()
        for word, score in keywords.items():
            if word in lower:
                return score
        return 5

    def _extract_topics(self, text: str) -> list[str]:
        topic_keywords = {
            "work": ["work", "job", "career", "boss", "colleague", "office"],
            "family": ["family", "parent", "mother", "father", "sibling", "child"],
            "relationships": ["relationship", "partner", "girlfriend", "boyfriend", "spouse", "date"],
            "health": ["health", "exercise", "sleep", "diet", "therapy", "medication"],
            "anxiety": ["anxious", "anxiety", "panic", "worry", "fear", "nervous"],
            "depression": ["depressed", "depression", "hopeless", "sad", "empty"],
            "self-esteem": ["confidence", "self-esteem", "worth", "insecure", "impostor"],
            "trauma": ["trauma", "abuse", "ptsd", "flashback", "trigger"],
        }
        lower = text.lower()
        found = []
        for topic, keywords in topic_keywords.items():
            if any(k in lower for k in keywords):
                found.append(topic)
        return found
