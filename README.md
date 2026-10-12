# La Liga de Agentes · Sesión 1

## Para estudiantes

1. Abre el repositorio en GitHub Codespaces (botón **Code → Codespaces → Create**). La instalación es automática.
2. Abre `.env` y pega los valores que te entregó el profe.
3. Verifica que todo funciona:

```bash
uv run python sesion1/golf.py
```

### Reto 1: Prompt Golf

Edita **solo** `sesion1/mi_prompt.txt`. Tu prompt debe contener `{mensaje}`, que es donde se inserta cada caso. Prueba con:

```bash
uv run python sesion1/golf.py                        # probar
uv run python sesion1/golf.py --verbose              # ver todas las salidas del modelo
uv run python sesion1/golf.py --equipo "Tu equipo"   # registrar un intento oficial
```

La salida del modelo debe ser solo el JSON `{"categoria": ..., "urgencia": ...}`, sin texto extra ni bloques de código. Gana quien acierte los 10 casos con menos tokens.

Reglas de urgencia: **alta** si hay un plazo de menos de 24 horas o riesgo de perder dinero o una nota; **media** si afecta un trámite sin plazo inmediato; **baja** si es una consulta informativa o el usuario dice que no es urgente. Categorías: `academico`, `financiero`, `tecnico`, `otro`.

### Reto 2: Protege a Biblio

Entra a la URL que comparte el profe, crea tu equipo con un PIN y sigue las instrucciones de la app.

---

## Para el profesor

### Antes de la clase

- **Modelo:** monta un LiteLLM Proxy con una llave virtual por equipo y un límite de gasto. Usa un modelo pequeño y que no sea de razonamiento (algunos rechazan `temperature`). Si prefieres no usar proxy, deja `LLM_BASE_URL` vacío y usa una llave de OpenAI directamente.
- **LangSmith:** crea un proyecto por equipo (`liga-equipo-01`, `liga-equipo-02`…) y reparte las llaves.
- **Casos ocultos:** la carpeta `profesor/` **no debe estar en el repositorio de los estudiantes**. Sácala antes de publicar.
- **Ensayo:** corre los dos retos de principio a fin con alguien una semana antes.

### Prompt Golf: validación final

Los equipos pueden "hacer trampa" sobreajustando su prompt a los 10 casos (por ejemplo, escribiendo las respuestas). Antes de declarar ganador, corre el prompt del equipo contra los casos ocultos:

```bash
uv run python sesion1/golf.py --prompt ruta/al/prompt.txt --casos profesor/casos_ocultos.json
```

Si un prompt acierta los visibles y falla los ocultos, aprovecha para hablar de sobreajuste: es exactamente lo que pasa con los modelos de ML.

Los intentos registrados con `--equipo` quedan en `sesion1/resultados_golf.csv` de cada Codespace; pide que te muestren el último o que lo copien en la tabla compartida.

### Protege a Biblio

Corre una sola instancia para todo el curso:

```bash
uv run streamlit run sesion1/biblio_app.py
```

En Codespaces, ve a la pestaña **Ports**, haz clic derecho en el puerto 8501 y cambia la visibilidad a **Public**. Comparte esa URL. Define `BIBLIO_ADMIN_PASSWORD` en tu `.env`.

Flujo sugerido desde la pestaña **Profesor**:

1. **Fase azul (15 min):** los equipos crean su cuenta, escriben el prompt y lo prueban.
2. **Prueba de utilidad:** al terminar la fase azul, pulsa el botón que hace las 3 preguntas legítimas a todos los Biblios y marca cuáles son útiles.
3. **Fase roja (20 min):** cada equipo tiene 10 intentos contra cada rival. Las filtraciones directas se detectan solas (incluso con espacios, guiones o al revés); las indirectas llegan como reclamos que tú confirmas o rechazas.
4. **Cerrar juego:** se otorgan los puntos de defensa y la tabla queda final.

Todos los datos se guardan en `sesion1/biblio.db`. Para repetir el reto con otro grupo, usa **Reiniciar el juego**.
