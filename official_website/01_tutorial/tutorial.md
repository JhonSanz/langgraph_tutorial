# Encadenamiento con edges, estado y nodos.

`self.tools_by_name = {tool.name: tool for tool in tools}`


Cada tool que pasas en la lista tools es un objeto de tipo Tool de LangChain.

Cuando creas un tool (ej: travily_tool), normalmente lo defines con algo como:

```python
from langchain_core.tools import tool

@tool
def travily_tool(query: str):
    """Busca información en Travily."""
    return {"result": f"Buscando {query}..."}
```


Ese decorador (@tool) convierte tu función en un objeto StructuredTool, y ese objeto siempre tiene atributos como:

- .name → el nombre de la herramienta (por defecto el nombre de la función, "travily_tool")
- .description → para que el LLM sepa qué hace
- .args_schema → qué argumentos acepta

👉 Entonces, cuando haces:

`{tool.name: tool for tool in tools}`


Estás construyendo un diccionario tipo:

```python
{
  "travily_tool": <StructuredTool travily_tool>,
  ...
}
```

Eso sirve para luego llamar a la herramienta correcta cuando el LLM diga "name": "travily_tool".

--- 

`inputs.get("messages", [])`

Esto pasa porque cada nodo del grafo recibe un diccionario con el state actual.
En tu caso, State es básicamente:

```python
from typing import TypedDict

class State(TypedDict):
    messages: list


State = TypedDict("State", {"messages": list})
```


y tu grafo siempre pasa el estado así:

`{"messages": [...]}`


#### Ejemplo en ejecución:

El usuario manda "hola" → tu grafo inicializa el state como:

`{"messages": [HumanMessage(content="hola")]}`


Ese diccionario va fluyendo entre nodos (chatbot, tools, etc).

En BasicToolNode.__call__, el nodo recibe ese diccionario y hace:

`inputs.get("messages", [])`


para acceder a la lista de mensajes y procesar el último.

👉 Es la manera estándar de leer el historial de mensajes que va cargando LangGraph.

--- 

`for tool_call in message.tool_calls`

Esto viene del AIMessage generado por el LLM cuando se le hace un .bind_tools(...).

#### Ejemplo:

Sin tools, el LLM devuelve un AIMessage con solo content.

Con tools, el LLM puede devolver un AIMessage con una lista en .tool_calls.

Esa propiedad .tool_calls la rellena LangChain automáticamente cuando el modelo responde con el formato de “invocar herramientas” (siguiendo el JSON schema que se le da en el binding).

Ejemplo de AIMessage con tool_calls:

```python
AIMessage(
  content="",
  tool_calls=[
    {
      "name": "travily_tool",
      "args": {"query": "últimas noticias de Ucrania"},
      "id": "call_123"
    }
  ]
)
```


Entonces:

route_tools revisa si el último mensaje (ai_message) tiene .tool_calls.

Si sí → lo manda al nodo "tools".

Si no → lo manda a END.

👉 En BasicToolNode, haces un loop:

```python
for tool_call in message.tool_calls:
    tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
```

Y eso ejecuta la función real de Python que corresponde a la herramienta.

✅ En resumen:

- tool.name → viene de cómo LangChain define las herramientas (StructuredTool).
- inputs["messages"] → es el estado que fluye en el grafo.
- .tool_calls → es un campo que LangChain mete en el AIMessage cuando el modelo pide usar una herramienta.




---


Entonces el flujo es:

1. El chatbot genera una respuesta.
2. route_tools mira el último mensaje.
   - Si hay tool_calls → devuelve "tools" (ese es el nodo BasicToolNode).
   - Si no hay → devuelve END.
3. El grafo consulta el mapa de resoluciones y dice:
   - "tools" → ir al nodo "tools".
   - END → terminar.
4. Una vez que se ejecuta el nodo "tools", agregaste este edge:
`graph_builder.add_edge("tools", "chatbot")`
o sea que al acabar un tool, el flujo vuelve al chatbot.