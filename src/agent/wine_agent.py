import json

from pydantic import BaseModel
from src.services.openai_client import model, client

class Agent():
    def __init__(self, instruction, tools=[], session_id='default', model=model, tool_choice='auto'):
        self.instruction = instruction
        self.model = model
        self.tool_choice = tool_choice
        self.user_sessions = {}


        pydantic_tools = []
        other_tools = []
        for tool in tools:
            if isinstance(tool, type) and issubclass(tool, BaseModel):
                pydantic_tools.append(tool)
            else:
                other_tools.append(tool)

        self.tool_map = {cls.__name__: cls for cls in pydantic_tools}
        self.tools = [self._create_tool_annot(cls) for cls in pydantic_tools] + other_tools

        print("Pydantic tools detected:", [cls.__name__ for cls in pydantic_tools])
        print("Tool map keys:", list(self.tool_map.keys()))

    def _create_tool_annot(self, x):
        if issubclass(x, BaseModel):
            return {
                "type": "function",
                "name": x.__name__,
                "description": x.__doc__,
                "parameters": x.model_json_schema(),
            }
        else:
            return x

    def __call__(self, message, session_id='default'):
        s = self.user_sessions.get(session_id, {'last_reply_id': None, 'history': []})
        s['history'].append({'role': 'user', 'content': message})

        try:
            res = client.responses.create(
                model=self.model,
                store=True,
                tools=self.tools,
                tool_choice=self.tool_choice,
                instructions=self.instruction,
                previous_response_id=s['last_reply_id'],
                input=message
            )
        except Exception as e:
            if "Previous response" in str(e):
                s['last_reply_id'] = None
                res = client.responses.create(
                    model=self.model,
                    store=True,
                    tools=self.tools,
                    tool_choice=self.tool_choice,
                    instructions=self.instruction,
                    previous_response_id=None,
                    input=message
                )
            else:
                raise e

        tool_calls = [item for item in res.output if item.type == "function_call"]
        if tool_calls:
            out = []
            for call in tool_calls:
                print(f" + Выполняю: {call.name} ({call.arguments!r})")
                try:
                    fn = self.tool_map[call.name]
                    raw_args = call.arguments
                    if not raw_args or raw_args.strip() in ("", "null"):
                        parsed_args = {}
                    else:
                        parsed_args = json.loads(raw_args)
                    obj = fn.model_validate(parsed_args)
                    result = obj.process(session_id)
                except Exception as e:
                    print(f"   [ОШИБКА ВЫЗОВА ИНСТРУМЕНТА] {e}")
                    result = f"Ошибка при выполнении {call.name}: {e}"
                out.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result
                })
            res = client.responses.create(
                model=self.model,
                input=out,
                tools=self.tools,
                previous_response_id=res.id,
                store=True
            )

        # Обработка MCP approval
        mcp_approve = [item for item in res.output if item.type == "mcp_approval_request"]
        if mcp_approve:
            approval_input = [
                {"type": "mcp_approval_response", "approve": True, "approval_request_id": m.id}
                for m in mcp_approve
            ]
            res = client.responses.create(
                model=self.model,
                previous_response_id=res.id,
                tools=self.tools,
                input=approval_input
            )

        s['last_reply_id'] = res.id
        s['history'].append({'role': 'assistant', 'content': res.output_text})
        self.user_sessions[session_id] = s
        return res

    def history(self, session_id='default'):
        return self.user_sessions[session_id]['history']
