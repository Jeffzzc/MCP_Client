from pprint import pprint
import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt.chat_agent_executor import create_react_agent

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="Query statement for executing Google search")

class DallEArgsSchema(BaseModel):
    query: str = Field(description="Input should be a text prompt for generating images")

google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "A low-cost Google search API. "
        "Use this tool when you need to answer questions about current events. "
        "The input for this tool is a search query."
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)

dalle = OpenAIDALLEImageGenerationTool(
    name="openai_dalle",
    api_wrapper=DallEAPIWrapper(model="dall-e-3"),
    args_schema=DallEArgsSchema,
)

tools = [google_serper, dalle]

model = ChatOpenAI(model="gpt-4o", temperature=0)

agent = create_react_agent(
    model=model,
    tools=tools
)

pprint(agent.invoke({"messages": [("human", "Help me draw a picture of a shark flying in the sky")]}))