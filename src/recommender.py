from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from src.prompt_template import get_yugioh_prompt

class YuGiOhRecommender:
    def __init__(self,retriever,api_key:str,model_name:str):
        self.llm = ChatGroq(api_key=api_key,model=model_name,temperature=0)
        self.retriever = retriever
        self.prompt = get_yugioh_prompt()

    def get_recommendation(self,query:str):
        # Retrieve relevant documents using the correct method name
        docs = self.retriever.invoke(query)

        # Combine context
        context = "\n\n".join([doc.page_content for doc in docs])

        # Create the prompt with context and question
        formatted_prompt = self.prompt.format(context=context, question=query)

        # Get response from LLM
        messages = [
            SystemMessage(content="You are an expert Yu-Gi-Oh! card recommender and strategist."),
            HumanMessage(content=formatted_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content
