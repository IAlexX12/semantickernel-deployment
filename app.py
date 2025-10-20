from flask import Flask, request, jsonify
import os
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatMessageContent, AuthorRole

app = Flask(__name__)

# Configuración de Azure OpenAI
DEPLOYMENT_NAME = "gpt-4o-mini"
AZURE_ENDPOINT = "https://aleja-mgqf97rj-swedencentral.services.ai.azure.com/"
AZURE_API_KEY = os.environ.get("OPENAI_API_KEY")

# Inicializar kernel y servicio
kernel = Kernel()
chat_service = AzureChatCompletion(
    deployment_name=DEPLOYMENT_NAME,
    endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY
)
kernel.add_service(chat_service)

# Crear el agente
agent = ChatCompletionAgent(
    name="AzureAgent",
    kernel=kernel,
    instructions="""
        Eres un asistente útil y conversacional que responde en español con explicaciones claras y breves.
        Si el usuario te saluda, responde con amabilidad.
    """
)

@app.route("/")
def home():
    return "Agente Azure OpenAI desplegado correctamente"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_message = data.get("prompt")

    if not user_message:
        return jsonify({"error": "Falta el campo 'prompt'"}), 400

    async def run_agent():
        # Crear mensaje del usuario sin historial
        messages = [ChatMessageContent(role=AuthorRole.USER, content=user_message)]

        # Invocar el agente
        async for response in agent.invoke(messages):
            # Devolver la respuesta del asistente
            if hasattr(response, "content") and isinstance(response.content, str):
                return response.content
            elif hasattr(response, "items") and len(response.items) > 0:
                return response.items[0].text
            else:
                return str(response)

    try:
        result = asyncio.run(run_agent())
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)






