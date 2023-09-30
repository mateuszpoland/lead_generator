from langchain import PromptTemplate, LLMMathChain
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.tools import BaseTool, Tool
from pydantic import BaseModel, Field
from typing import Type
from bs4 import BeautifulSoup
import requests
import json
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
browserless_api_key = os.getenv("BROWSERLESS_API_KEY")

model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

class ProcessingInput(BaseModel):
    """Inputs for scrape_website"""
    wikipediaUrl: str = Field(description="Wikipedia url for scraping")
    country: str = Field(description="Country name for which the wikipedia page is being scraped")

class Scraper():
    def scrape(self, url: str) -> str:
        print(f"scraping {url} content".format(url))
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }

        payload = json.dumps({"url": url})
        post_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
        response = requests.post(post_url, headers=headers, data=payload)
        if response.status_code != 200:
            return (f"HTTP request failed with status code {response.status_code}")
        
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        return text

class USAWikipediaProcessor():
    def __init__(self) -> None:
        self.model = model
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n", "\n\n"],
            chunk_size=10000,
            chunk_overlap=1000,
        )

    def generateListOfPlaces(self, content: str) -> str:
        template = """
        %INSTRUCTIONS:
        Given the contents which is a scraped Wikipedia page, extract a list of places mentioned in the page.
        These will be under <span class="mw-headline" id="Communities>Communities</span> in the output There will be a list of <h3> tags where there will be links containing the place name which need to be extracted.
        Example: <a href="/w/index.php?title=Andrews_County,_Texas&amp;action=edit&amp;section=9" title="Edit section: Communities">edit</a>
        The place name is Andrews County, Texas and you need to extract it in the format Andrews County, Texas. Extract all of the places contained in the section. Output them in a 
        %TEXT:
        {content}
        """

        num_tokens = self.model.get_num_tokens(content)
        docs = self.text_splitter.create_documents([content])

        prompt = PromptTemplate.from_template(template)
        prompt.format(content=content)

        extraction_chain = load_summarize_chain(
            llm=self.model,
            chain_type='map_reduce',
            verbose=True,
        )

        output = extraction_chain.run(docs)
        print(output)
        return output


class LLMJsonOutputFormatter():
    def __init__(self) -> None:
        self.responseSchemas = [
            ResponseSchema(name="places", description="")
        ]

    def formatJson(output: str) -> str:
        
        

class ScrapeAndExtractPlacesTool(BaseTool):
    name="scrape_and_extract_places"
    description="useful when you have a wikipedia url and the task is to scrape the page and extract places(cities, villages, communities etc.) mentioned in the page"
    args_schema: Type[BaseModel] = ProcessingInput
    scraper = Scraper()
    processors={
        "USA": USAWikipediaProcessor()
    }

    def _run(self, wikipediaUrl: str, country: str) -> str:
        content = self.scraper.scrape(wikipediaUrl)
        processor = self.processors[country]

        return processor.generateListOfPlaces(content)

    def _arun(self, url: str):
        raise NotImplementedError("This tool does not support asynchronous run")

#create langchain agent
tools = [
    ScrapeAndExtractPlacesTool()
]

agent_kwargs = {
    "system_message": SystemMessage(content="You are a web scraper bot with the knowledge of extracting places from a wikipedia page. You can scrape a wikipedia page and extract places from it.")
}

agent = initialize_agent(
    llm=model,
    tools=tools,
    model=model,
    verbose=True,
    agent_kwargs=agent_kwargs,
    agent=AgentType.OPENAI_FUNCTIONS
)

class Agent():
    def __init__(self) -> None:
        self.agent = agent

    def process(self, country: str, url: str) -> str:
        
        response = self.agent({"input": f"Process this wikipedia page which url is: {url} for country {country} and extract places from it".format(url, country)})

        return response["output"]
    