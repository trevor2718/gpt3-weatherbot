from langchain.llms import OpenAI
from dotenv import dotenv_values
from langchain import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate


config = dotenv_values(".env") 
OpenAI.api_key = config["openapi_key"]

class ChatBot:
    def __init__(self,template):
        self.template = template
        self.history = ""

        self.prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"], 
            template=template
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)
    
        llm_chain = LLMChain(
                        llm=OpenAI(temperature=0.0,), 
                        prompt=self.prompt, 
                        verbose=True, 
                        memory=self.memory,
                    )
        self.agent = llm_chain
        return 
    
    def get_reply(self,message):
        """
        for the given input message from user get the reply of the chatbot 
        """
        reply = self.agent.predict(human_input=message)

        return reply