import math
import re
from collections import Counter
from pathlib import Path


class RAGService:

    def __init__(
        self,
        knowledge_path: str | None = None
    ):
        if knowledge_path:
            self.knowledge_path = Path(
                knowledge_path
            )
        else:
            project_root = Path(
                __file__
            ).resolve().parents[2]

            self.knowledge_path = (
                project_root / "knowledge"
            )

        if not self.knowledge_path.exists():
            raise ValueError(
                "Knowledge directory does not exist: "
                f"{self.knowledge_path}"
            )

        self.chunks = self._load_chunks()

        if not self.chunks:
            raise ValueError(
                "No knowledge documents were found"
            )

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:

        if not query.strip():
            raise ValueError(
                "RAG query cannot be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        document_frequency = (
            self._build_document_frequency()
        )

        query_tokens = self._tokenize(query)

        query_vector = self._build_tfidf_vector(
            query_tokens,
            document_frequency
        )

        results = []

        for chunk in self.chunks:
            chunk_tokens = self._tokenize(
                chunk["content"]
            )

            chunk_vector = self._build_tfidf_vector(
                chunk_tokens,
                document_frequency
            )

            score = self._cosine_similarity(
                query_vector,
                chunk_vector
            )

            if score <= 0:
                continue

            results.append({
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "score": round(score, 4)
            })

        results.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        return results[:top_k]

    def list_documents(self) -> list[str]:
        documents = {
            chunk["source"]
            for chunk in self.chunks
        }

        return sorted(documents)

    def _load_chunks(self) -> list[dict]:
        chunks = []

        supported_extensions = (
            "*.md",
            "*.txt"
        )

        document_paths = []

        for extension in supported_extensions:
            document_paths.extend(
                self.knowledge_path.glob(
                    extension
                )
            )

        for document_path in sorted(
            document_paths
        ):
            content = document_path.read_text(
                encoding="utf-8"
            )

            document_chunks = self._split_text(
                content
            )

            for index, chunk_content in enumerate(
                document_chunks,
                start=1
            ):
                chunks.append({
                    "source": document_path.name,
                    "chunk_id": index,
                    "content": chunk_content
                })

        return chunks

    @staticmethod
    def _split_text(
        content: str
    ) -> list[str]:

        raw_chunks = re.split(
            r"\n\s*\n",
            content
        )

        chunks = []

        for raw_chunk in raw_chunks:
            clean_chunk = raw_chunk.strip()

            if clean_chunk:
                chunks.append(clean_chunk)

        return chunks

    @staticmethod
    def _tokenize(
        text: str
    ) -> list[str]:

        tokens = re.findall(
            r"[a-zA-Z0-9_]+",
            text.lower()
        )

        return [
            token
            for token in tokens
            if len(token) > 2
        ]

    def _build_document_frequency(
        self
    ) -> dict[str, int]:

        document_frequency = Counter()

        for chunk in self.chunks:
            unique_tokens = set(
                self._tokenize(
                    chunk["content"]
                )
            )

            for token in unique_tokens:
                document_frequency[token] += 1

        return dict(document_frequency)

    def _build_tfidf_vector(
        self,
        tokens: list[str],
        document_frequency: dict[str, int]
    ) -> dict[str, float]:

        term_frequency = Counter(tokens)

        total_tokens = len(tokens)

        if total_tokens == 0:
            return {}

        total_documents = len(self.chunks)

        vector = {}

        for token, count in term_frequency.items():
            tf_value = count / total_tokens

            document_count = (
                document_frequency.get(
                    token,
                    0
                )
            )

            idf_value = math.log(
                (
                    total_documents + 1
                ) / (
                    document_count + 1
                )
            ) + 1

            vector[token] = (
                tf_value * idf_value
            )

        return vector

    @staticmethod
    def _cosine_similarity(
        first_vector: dict[str, float],
        second_vector: dict[str, float]
    ) -> float:

        shared_tokens = (
            set(first_vector)
            & set(second_vector)
        )

        dot_product = sum(
            first_vector[token]
            * second_vector[token]
            for token in shared_tokens
        )

        first_norm = math.sqrt(
            sum(
                value * value
                for value in first_vector.values()
            )
        )

        second_norm = math.sqrt(
            sum(
                value * value
                for value in second_vector.values()
            )
        )

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return (
            dot_product
            / (first_norm * second_norm)
        )