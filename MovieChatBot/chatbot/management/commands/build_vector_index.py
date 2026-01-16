from django.core.management.base import BaseCommand
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from tmdb_api.models import Movie
from reviews.models import Review

VS_DIR = "vector_store"

class Command(BaseCommand):
    help = "Build vector index from Movie + Review"

    def handle(self, *args, **options):
        docs = []

        for m in Movie.objects.all():
            text = (
                f"[MOVIE]\n"
                f"제목: {m.title}\n"
                f"개봉: {m.release_date}\n"
                f"장르: {m.genre}\n"
                f"감독: {m.director}\n"
                f"주연: {m.leadActor}\n"
                f"줄거리: {m.overview}\n"
            )
            docs.append(Document(page_content=text, metadata={
                "type": "movie",
                "movie_id": m.id,
                "tmdb_id": m.tmdb_id,
            }))

        for r in Review.objects.select_related("movie").all():
            mt = r.movie.title if r.movie else ""
            text = (
                f"[REVIEW]\n"
                f"영화: {mt}\n"
                f"평점: {r.rating}\n"
                f"리뷰제목: {r.title}\n"
                f"내용: {r.content}\n"
            )
            docs.append(Document(page_content=text, metadata={
                "type": "review",
                "review_id": r.id,
            }))

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120
        )
        splits = splitter.split_documents(docs)

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=VS_DIR,
        )

        self.stdout.write(self.style.SUCCESS("Vector index build complete"))
