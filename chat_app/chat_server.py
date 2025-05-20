from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mcp_client import MCPClient, MCP_SERVER_PATH
from contextlib import asynccontextmanager
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage


@asynccontextmanager
async def lifespan(app: FastAPI):
    agent = MCPClient()
    await agent.connect_to_mcp_server(MCP_SERVER_PATH)
    app.state.agent = agent
    yield 

    await app.state.agent.cleanup()


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

chat_history: list[dict] = []


def get_agent(request: Request) -> MCPClient:
    return request.app.state.agent


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "messages": chat_history})


@app.post("/send", response_class=HTMLResponse)
async def send_message(request: Request, message: str = Form(...), agent: MCPClient = Depends(get_agent)):
    user_msg = {"role": "user", "content": message}
    chat_history.append(user_msg)

    response = await agent.process_query(message)
    response_messages = response.get('messages', [])
    tool_steps = []
    final_answer = None 
    for m in response_messages:
        match m:
            case ToolMessage(content=c, name=n):
                tool_steps.append(f"Tool <strong>{n}</strong> returned <br><code>{c}</code>")
            case AIMessage(content=c, name=n) if c:
                final_answer = m.content
            case HumanMessage():
                continue
            case _:
                continue

    html_content = f"""
        <div><strong>Assistant Reasoning:</strong></div>
        <ul>
            {''.join(f'<li>{step}</li>' for step in tool_steps)}
        </ul>
        <div><strong>Final Answer:</strong> {final_answer or '[No answer yet]'}</div>
    """
    ai_msg = {"role": "assistant", "content": html_content}
    chat_history.append(ai_msg)

    return templates.TemplateResponse("chat_message.html", {
        "request": request,
        "messages": [user_msg, ai_msg]
    })


@app.post("/clear", response_class=HTMLResponse)
async def clear_chat(request: Request):
    chat_history.clear()
    return templates.TemplateResponse("chat_message.html", {
        "request": request,
        "messages": []
    })
