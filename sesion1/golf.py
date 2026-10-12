"""Prompt Golf: evalúa tu prompt contra los casos de prueba.

Uso:
    uv run python sesion1/golf.py                      # prueba sesion1/mi_prompt.txt
    uv run python sesion1/golf.py --equipo "Los Tensores"   # además registra el resultado
    uv run python sesion1/golf.py --casos profesor/casos_ocultos.json  # validación final

Reglas:
  - Tu prompt debe contener el marcador {mensaje}; ahí se inserta cada caso.
  - La salida del modelo debe ser SOLO el JSON, sin texto extra ni ```.
  - Gana quien acierte todos los casos con menos tokens de prompt.
"""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import tiktoken

from llm import get_llm, texto

AQUI = Path(__file__).resolve().parent
MARCADOR = "{mensaje}"
LLAVES = {"categoria", "urgencia"}


def contar_tokens(plantilla: str) -> int:
    """Tokens del prompt del equipo, sin contar el mensaje insertado.

    Se usa un tokenizador fijo para que el conteo sea igual para todos,
    sin importar qué modelo esté detrás del proxy.
    """
    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(plantilla.replace(MARCADOR, "")))


def evaluar_salida(salida: str, esperado: dict) -> tuple[bool, str]:
    try:
        datos = json.loads(salida.strip())
    except json.JSONDecodeError:
        return False, "no es JSON puro (¿texto extra o bloque ```?)"
    if not isinstance(datos, dict) or set(datos) != LLAVES:
        return False, f"llaves incorrectas: debe tener exactamente {sorted(LLAVES)}"
    if datos != esperado:
        return False, f"esperaba {esperado['categoria']}/{esperado['urgencia']}"
    return True, "ok"


def registrar(equipo: str, aciertos: int, total: int, tokens: int, casos: Path) -> Path:
    archivo = AQUI / "resultados_golf.csv"
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "equipo", "aciertos", "total", "tokens", "casos"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), equipo,
                    aciertos, total, tokens, casos.name])
    return archivo


def main() -> int:
    p = argparse.ArgumentParser(description="Prompt Golf")
    p.add_argument("--prompt", type=Path, default=AQUI / "mi_prompt.txt")
    p.add_argument("--casos", type=Path, default=AQUI / "casos.json")
    p.add_argument("--equipo", help="nombre del equipo para registrar el intento")
    p.add_argument("--verbose", action="store_true", help="muestra la salida cruda del modelo")
    args = p.parse_args()

    plantilla = args.prompt.read_text(encoding="utf-8")
    if MARCADOR not in plantilla:
        print(f"Tu prompt debe incluir el marcador {MARCADOR}.")
        return 1

    casos = json.loads(args.casos.read_text(encoding="utf-8"))
    llm = get_llm(temperature=0)
    tokens = contar_tokens(plantilla)

    print(f"\nPrompt: {args.prompt.name}  |  {tokens} tokens  |  {len(casos)} casos\n")
    aciertos = 0
    for i, caso in enumerate(casos, start=1):
        # replace (no .format) para que las llaves de un JSON de ejemplo no rompan nada
        prompt = plantilla.replace(MARCADOR, caso["mensaje"])
        salida = texto(llm.invoke(prompt))
        ok, motivo = evaluar_salida(salida, caso["esperado"])
        aciertos += ok
        marca = "✅" if ok else "❌"
        print(f"{marca} {i:>2}. {caso['mensaje'][:60]:<60}  {motivo}")
        if args.verbose or not ok:
            print(f"       salida: {salida.strip()[:150]!r}")

    total = len(casos)
    print(f"\nResultado: {aciertos}/{total} aciertos con {tokens} tokens")
    if aciertos == total:
        print("Clasifica para el ranking. Ahora intenta recortar tokens.")
    else:
        print("Aún no clasifica: necesitas acertar todos los casos.")

    if args.equipo:
        archivo = registrar(args.equipo, aciertos, total, tokens, args.casos)
        print(f"Intento registrado en {archivo.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
