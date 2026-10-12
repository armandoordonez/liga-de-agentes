"""Acceso al modelo compartido por todo el taller.

Todos los equipos usan el MISMO modelo (configurado en .env) para que
las competencias sean justas. Las llamadas quedan trazadas en LangSmith
automáticamente si LANGSMITH_TRACING=true.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_llm(temperature: float = 0.0, max_tokens: int = 400) -> ChatOpenAI:
    faltantes = [v for v in ("LLM_MODEL", "LLM_API_KEY") if not os.getenv(v)]
    if faltantes:
        raise RuntimeError(
            f"Faltan variables en .env: {', '.join(faltantes)}. "
            "Copia .env.example como .env y llénalo."
        )
    return ChatOpenAI(
        model=os.environ["LLM_MODEL"],
        api_key=os.environ["LLM_API_KEY"],
        base_url=os.getenv("LLM_BASE_URL") or None,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=3,
    )


def texto(respuesta) -> str:
    """Extrae el texto de una respuesta, sea str o lista de bloques."""
    contenido = respuesta.content
    if isinstance(contenido, str):
        return contenido
    partes = []
    for bloque in contenido:
        if isinstance(bloque, str):
            partes.append(bloque)
        elif isinstance(bloque, dict) and bloque.get("type") == "text":
            partes.append(bloque.get("text", ""))
    return "".join(partes)
