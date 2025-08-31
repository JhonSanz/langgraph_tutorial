from app.graph import graph
from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv()


def stream_graph_updates(user_input: str, is_resume: bool = False):
    config = {"configurable": {"thread_id": "1"}}

    if is_resume:
        # Aquí metes la respuesta humana (resume)
        command = Command(resume={"data": user_input})
        events = graph.stream(command, config, stream_mode="values")
    else:
        # Input normal del usuario
        command = {"messages": [{"role": "user", "content": user_input}]}
        events = graph.stream(command, config, stream_mode="values")

    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()


if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Si el usuario empieza con /resume, lo tratamos como reanudación
        if user_input.startswith("/resume "):
            stream_graph_updates(user_input.replace("/resume ", ""), is_resume=True)
        else:
            stream_graph_updates(user_input)
