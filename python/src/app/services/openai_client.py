import os
import json
import logging
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_key_raw = os.getenv("OPENAI_API_KEY")
if not api_key_raw:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

api_key = SecretStr(api_key_raw)


api_version = os.getenv("OPENAI_API_VERSION")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
if azure_endpoint is None:
    raise ValueError("AZURE_ENDPOINT is not set")
chat_deployment = os.getenv("OPENAI_AZURE_DEPLOYMENT")
embedding_deployment = os.getenv("OPENAI_AZURE_EMBEDDING_DEPLOYMENT")
if embedding_deployment is None:
    raise ValueError("AZURE_ENDPOINT is not set")


try:
    chat_model = AzureChatOpenAI(
        azure_deployment=chat_deployment,
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
        temperature=0
    )

    aoai_client = AzureOpenAI(
        api_key=api_key.get_secret_value(),  
        api_version=api_version,
        azure_endpoint=azure_endpoint,
    )

    logger.info("Azure OpenAI clients initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Azure OpenAI clients: {e}")
    raise


def generate_embedding(text: str) -> list:
    try:
        response = aoai_client.embeddings.create(
            input=text,
            model=str(embedding_deployment)
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


if __name__ == "__main__":
    
    try:
        response = chat_model.invoke("Say hello from Azure OpenAI")
        print("[TEST] Chat response:", response.content)
    except Exception as e:
        logger.error(f"[TEST] Chat completion failed: {e}")

    
    try:
        test_embedding = generate_embedding("Test embedding from Azure OpenAI")
        print("[TEST] Embedding vector length:", len(test_embedding))
    except Exception as e:
        logger.error(f"[TEST] Embedding generation failed: {e}")
