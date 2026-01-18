from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

VS_DIR = "vector_store"

client = OpenAI()

def retrieve_context(query: str, k: int = 6) -> str:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    vs = Chroma(
        persist_directory=VS_DIR,
        embedding_function=embeddings,
    )

    docs = vs.similarity_search(query, k=k)

    # 토큰 절약: 각 문서 200자 제한
    return "\n\n".join(d.page_content[:200] for d in docs)



def generate_answer(user_query: str, context: str) -> str:
    system_prompt = (
        "너는 영화 추천 AI다.\n"
        "- 반드시 한국어로 답한다.\n"
        "- 아래 컨텍스트는 사용자의 취향 근거다.\n"
        "- 컨텍스트를 참고해 영화 3~5개를 추천한다.\n"
        "- 형식: 제목 / 한줄 이유"
    )

    resp = client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {"role": "developer", "content": system_prompt},
            {"role": "user", "content": f"[컨텍스트]\n{context}\n\n[질문]\n{user_query}"},
        ],
    )
    return resp.output_text
