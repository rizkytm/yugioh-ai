from src.vector_store import VectorStoreBuilder
from src.recommender import YuGiOhRecommender
from config.config import GROQ_API_KEY,MODEL_NAME
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

class YuGiOhRecommendationPipeline:
    def __init__(self,persist_dir="chroma_db"):
        try:
            logger.info("Initializing Yu-Gi-Oh! Recommendation Pipeline")

            vector_builder = VectorStoreBuilder(csv_path="" , persist_dir=persist_dir)

            retriever = vector_builder.load_vector_store().as_retriever()

            self.recommender = YuGiOhRecommender(retriever,GROQ_API_KEY,MODEL_NAME)

            logger.info("Yu-Gi-Oh! Pipeline initialized successfully...")

        except Exception as e:
            logger.error(f"Failed to initialize Yu-Gi-Oh! pipeline {str(e)}")
            raise CustomException("Error during Yu-Gi-Oh! pipeline initialization" , e)

    def recommend(self,query:str) -> str:
        try:
            logger.info(f"Received Yu-Gi-Oh! query: {query}")

            recommendation = self.recommender.get_recommendation(query)

            logger.info("Yu-Gi-Oh! recommendation generated successfully...")
            return recommendation
        except Exception as e:
            logger.error(f"Failed to get Yu-Gi-Oh! recommendation {str(e)}")
            raise CustomException("Error during Yu-Gi-Oh! recommendation" , e)
