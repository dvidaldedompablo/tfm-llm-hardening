# Bastionado de LLMs locales

Código del Trabajo Fin de Máster **"Securización y bastionado de grandes modelos de lenguaje (LLMs) desplegados en entornos locales"**, del Máster Universitario en Seguridad de las Tecnologías de la Información y las Comunicaciones de la Universidad Europea.

- **Autor:** Daniel Vidal de Dompablo
- **Director:** Daniel Fírvida Pereira
- **Estado:** defendido en octubre de 2026

## Qué hay en este repositorio

Un laboratorio que cualquiera puede montar en su ordenador para atacar un modelo de lenguaje que funciona en local y comprobar si unas defensas sencillas lo protegen.

El modelo hace de asistente de una empresa ficticia (ACME) y tiene en su contexto una clave interna que no debe revelar. Los ataques intentan que la revele, que enseñe sus instrucciones internas o que se salte sus reglas.

**Antes de leer los resultados:** la batería de pruebas tiene solo siete ataques, y cada uno se lanzó una vez. Es una muestra demasiado pequeña para sacar conclusiones generales sobre la seguridad del sistema. El apartado [Limitación principal](#limitación-principal-el-tamaño-de-la-muestra) explica qué se puede afirmar con estos datos y qué no.

## Cómo está montado

El laboratorio usa dos contenedores Docker:

- **`ollama`**: sirve el modelo Llama 3.2 de 3B parámetros. Su puerto no se publica fuera de Docker, así que solo la aplicación puede hablar con el modelo.
- **`llm-app`**: aplicación en FastAPI que recibe las preguntas, aplica las defensas y llama al modelo. Escucha en el puerto 8000.

Las defensas se activan o se desactivan con la variable `HARDENING` de `docker-compose.yml`. Así se puede lanzar la misma batería de ataques contra el sistema con y sin defensas.

| Capa | Archivo | Qué hace |
|---|---|---|
| 1. Instrucciones de sistema reforzadas | `app/system_prompts.py` | Reglas que indican al modelo qué no debe revelar ni hacer. |
| 2. Filtro de entrada | `app/input_guard.py` | Once expresiones regulares que buscan patrones de ataque conocidos. Antes de comparar, traduce el leetspeak y decodifica el texto en Base64 para que el ataque no pueda esconderse. |
| 3. Filtro de salida | `app/output_guard.py` | Revisa la respuesta del modelo antes de entregarla y la bloquea si contiene información que no debe salir. |
| 4. Juez LLM (descartada) | `app/llm_judge.py` | Usaba el propio modelo para decidir si una pregunta era un ataque. Se probó y se descartó porque un modelo de 3B no distinguía los ataques de forma fiable. El código se mantiene porque este resultado negativo forma parte del trabajo. |

## Cómo montarlo

Necesitas Docker Desktop, unos 8 GB de RAM libres y Python 3 con la librería `requests` para lanzar los ataques.

```bash
docker compose up -d --build
docker exec -it ollama ollama pull llama3.2:3b
```

Para comprobar que funciona:

```bash
curl http://localhost:8000/health
```

También hay una pequeña interfaz web en `http://localhost:8000`.

## Cómo lanzar los ataques

Los ataques están en `redteam/attacks.json`. Cada uno indica su categoría del OWASP Top 10 para aplicaciones con LLM (2025) y los textos que, si aparecen en la respuesta, significan que el ataque ha tenido éxito.

```bash
pip install requests
cd redteam
python red_team.py ../resultados/results_baseline.json
```

El script clasifica cada ataque en uno de tres estados:

- **Comprometido:** el modelo hizo lo que pedía el ataque.
- **Resistido:** el ataque llegó al modelo, pero el modelo no cayó.
- **Bloqueado:** una de las defensas paró el ataque antes o después del modelo.

## Resultados

| Prueba | Resultado |
|---|---|
| Ataques con éxito sin defensas | 1 de 7 (A1) |
| Ataques con éxito con defensas | 0 de 7 |
| Preguntas legítimas bloqueadas por error | 0 de 5 |

Los resultados completos están en la carpeta `resultados/`, junto con las gráficas de comparación.

Llama 3.2 ya resiste muchos ataques sin ninguna defensa añadida, gracias a su propio entrenamiento. Por eso el punto de partida es 1 de 7 y no un número más alto.

## Limitación principal: el tamaño de la muestra

Siete ataques, lanzados una sola vez cada uno, son pocos para concluir que el sistema es seguro. Esta fue también la principal observación de la comisión evaluadora en la defensa.

**Qué se puede afirmar con estos datos:**

- El laboratorio funciona y permite comparar el mismo sistema con y sin defensas.
- Las defensas frenaron los siete ataques probados, que cubren cinco categorías del OWASP Top 10 para aplicaciones con LLM.
- Las defensas no bloquearon ninguna de las cinco preguntas legítimas de prueba.

**Qué no se puede afirmar:**

- Que el sistema resista cualquier ataque de esas categorías. Cada categoría tiene muchas variantes y aquí se probaron una o dos por categoría.
- Que la tasa de éxito real sea 0 %. El modelo no siempre responde igual a la misma pregunta, así que un ataque que falló una vez puede tener éxito en otro intento.
- Que la tasa de falsos positivos sea 0 %. Cinco preguntas legítimas tampoco son suficientes para medirla.

**Qué haría falta para sacar conclusiones generales:**

- Una batería mucho mayor, con decenas de variantes por categoría (reformulaciones, otros idiomas, ataques en varios pasos).
- Repetir cada ataque varias veces y medir con qué frecuencia tiene éxito, en lugar de anotar un único resultado.
- Un conjunto más amplio de preguntas legítimas para medir los falsos positivos.
- Herramientas de pruebas automáticas para LLMs que generen y lancen esas variantes.

## Otras limitaciones

- **Dos patrones del filtro de entrada no funcionan.** Los patrones `CLAVE_INTERNA` y `\bDAN\b` están escritos en mayúsculas, pero el filtro pasa el texto a minúsculas antes de compararlo. Por eso nunca saltan, y el resultado de A6 con defensas no depende de ellos. Se corrige comparando sin distinguir mayúsculas y minúsculas. No se ha cambiado en este repositorio para que el código coincida con el que produjo los resultados de la memoria.
- **Filtros basados en patrones.** Un atacante que reformule la petición con otras palabras puede esquivar el filtro de entrada. Por eso el sistema usa varias capas y no depende solo de una.
- **Un único modelo.** Todas las pruebas se hicieron con Llama 3.2 de 3B. Otros modelos pueden comportarse de forma distinta.

## Trabajo futuro

- Ampliar la batería de ataques y repetir cada uno varias veces, como se describe en la limitación principal.
- Corregir los dos patrones del filtro de entrada y repetir las pruebas.
- Llevar el mismo enfoque a agentes de IA que usan herramientas externas.

## Aviso

La empresa ACME y la clave interna que aparece en el código son ficticias. Este laboratorio tiene fines académicos.
