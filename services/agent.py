import json
from typing import Any, Dict, List, Union
from openai import OpenAI

from config import FOLDER_ID, API_KEY, BASE_URL, MODEL_NAME
from models import Handover, AddToCart, ShowCart

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, project=FOLDER_ID)

TOOL_MAP = {
    "Handover": Handover,
    "AddToCart": AddToCart,
    "ShowCart": ShowCart,
}


class Agent:
    def __init__(self, instruction: str, tools: List[Union[dict, type]]):
        self.instruction = instruction
        self.model = f"gpt://{FOLDER_ID}/{MODEL_NAME}/latest"
        self.tool_choice = "auto"
        self.tools = self._build_tools(tools)
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

    def _build_tools(self, tools):
        result = []
        for t in tools:
            if isinstance(t, type):
                result.append({
                    "type": "function",
                    "name": t.__name__,
                    "description": t.__doc__ or "",
                    "parameters": t.model_json_schema(),
                })
            else:
                result.append(t)
        return result

    def __call__(self, message: str, session_id: str = "default"):
        session = self.user_sessions.setdefault(session_id, {"last_reply_id": None, "history": []})
        session["history"].append({"role": "user", "content": message})

        res = self._create_response(message, session["last_reply_id"])

        tool_calls = [item for item in res.output if item.type == "function_call"]
        if tool_calls:
            outputs = []
            for call in tool_calls:
                fn_class = TOOL_MAP.get(call.name)
                if fn_class:
                    try:
                        obj = fn_class.model_validate(json.loads(call.arguments))
                        output = obj.process(session_id)
                    except Exception as e:
                        output = f"Ошибка: {e}"
                else:
                    output = "Неизвестная функция"
                outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": output
                })
            res = self._create_response(outputs, res.id)

        mcp_requests = [item for item in res.output if item.type == "mcp_approval_request"]
        if mcp_requests:
            approval_input = [
                {"type": "mcp_approval_response", "approve": True, "approval_request_id": r.id}
                for r in mcp_requests
            ]
            res = self._create_response(approval_input, res.id)

        session["last_reply_id"] = res.id
        session["history"].append({"role": "assistant", "content": res.output_text})
        if not res.output_text or not res.output_text.strip():
            print(f"⚠️ Пустой output_text для session={session_id}, input={message}")
            print(f"   Raw output: {res.output}")
        return res

    def _create_response(self, input_data, previous_id):
        try:
            return client.responses.create(
                model=self.model,
                store=True,
                tools=self.tools,
                tool_choice=self.tool_choice,
                instructions=self.instruction,
                previous_response_id=previous_id,
                input=input_data
            )
        except Exception as e:
            if "Previous response" in str(e) and previous_id is not None:
                return client.responses.create(
                    model=self.model,
                    store=True,
                    tools=self.tools,
                    tool_choice=self.tool_choice,
                    instructions=self.instruction,
                    previous_response_id=None,
                    input=input_data
                )
            raise
