import json
import ollama
import spinner
import tools
import settings

class LLM:
    short_answer = True
    primer = settings.PRIMER
    messages = primer

    def call_tools(self, fn_name, fn_args):

        result = tools.get_function_by_name(fn_name)(**fn_args)

        # Print the Wikipedia content in a formatted way
        if result["status"] == "success":
            print("tool-call OK\n")
        else:
            print("tool-call FAILED\n")

        self.messages.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "name": fn_name,
            }
        )

    def generate_response(self):

        if(self.short_answer):
            messages_a=self.messages+[{"role": "system", "content": "Answer as a friendly and cute woman. Answer short and precise."}]
        else:
            messages_a=self.messages+[{"role": "system", "content": "Answer as a friendly and cute woman. Answer precisely."}]

        with spinner.Spinner("Thinking..."):
            #text = tokenizer.apply_chat_template(messages_a, tools=tools, add_generation_prompt=True, tokenize=False)
            response = ollama.chat(
                model= settings.LLM_MODEL,
                messages= messages_a,
                tools= tools.get_tools(),
                keep_alive= 0,
            )
            self.messages.append({"role": "assistant", "content": response.message.content})

        if response.message.tool_calls:
            # Handle tool calls
            for tool in response.message.tool_calls:
                self.call_tools(tool.function.name, tool.function.arguments)
            return(self.generate_response())
            
        else:
            # Handle regular response
            message=self.messages[-1].get("content")
            print(message)
            return(message)
        
    def message(self, input, _=""):
        user_input = input.strip()
        if "goodbye" in user_input.lower():
            global exit
            exit=True

        self.messages.append({"role": "user", "content": user_input})

        res=self.generate_response()

        return(res)