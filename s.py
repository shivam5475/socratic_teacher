from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.callbacks import get_openai_callback
from langchain_community.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class SocraticTeacher:
    def __init__(self, api_key=None):
        """Initialize the Socratic Teacher with API key"""
        self.api_key = api_key
        self.llm = self._create_llm()
        self.memory = self._setup_memory()
        self.chain = self._setup_chain()
        self.search = self._setup_search()
        
    def _create_llm(self):
        """Create LLM instance with configuration"""
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_tokens=2000,
            top_p=0.95,
            top_k=40,
            timeout=30,
            max_retries=3,
            google_api_key=self.api_key
        )

    def _setup_memory(self):
        """Setup enhanced memory with summary capability"""
        return ConversationSummaryMemory(
            llm=self.llm,
            max_token_limit=2000,
            return_messages=True,
            memory_key="chat_history",
            input_key="input",
            output_key="output"
        )

    def _setup_search(self):
        """Setup Google Search capability"""
        try:
            return GoogleSearchAPIWrapper(google_api_key=self.api_key)
        except Exception:
            return None

    def _setup_chain(self):
        """Setup the conversation chain with system message and memory"""
        system_template = """You are an AI-Powered Socratic Teacher. Your role is to:

1. Guide learners using the Socratic method
2. Ask thought-provoking questions based on real-world examples
3. Help students discover answers through reasoning
4. Adapt your questions based on student responses
5. Maintain a warm, encouraging tone
6. Use analogies and examples to clarify complex concepts
7. Break down complex topics into manageable parts
8. Celebrate student insights and progress

When teaching:
- Ask one focused question at a time
- Build on previous answers
- Use real-world examples
- Encourage critical thinking
- Provide gentle guidance when needed
- Maintain a positive learning environment
- Draw connections between concepts
- Help students develop metacognitive skills

Chat History: {chat_history}
Student Input: {input}
Additional Context: {context}

Remember to:
1. Acknowledge the student's response
2. Build on their understanding
3. Ask a thoughtful follow-up question
4. Use relevant examples

Your response:"""

        prompt = PromptTemplate(
            input_variables=["chat_history", "input", "context"],
            template=system_template
        )

        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )

    def _get_additional_context(self, query):
        """Get additional context from Google Search if available"""
        try:
            if self.search:
                search_results = self.search.run(query)
                return search_results[:500]  # Limit context size
            return ""
        except Exception:
            return ""

    def get_response(self, learner_input):
        """Get response from the Socratic Teacher"""
        try:
            # Get additional context if available
            context = self._get_additional_context(learner_input)
            
            # Generate response using the chain
            response = self.chain.run(
                input=learner_input,
                context=context
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory = self._setup_memory()
        self.chain = self._setup_chain()

# Function to create a new instance of SocraticTeacher
def create_teacher(api_key=None):
    return SocraticTeacher(api_key)
