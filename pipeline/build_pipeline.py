import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import YuGiOhDataLoader
from src.vector_store import VectorStoreBuilder
from dotenv import load_dotenv
from utils.logger import get_logger
from utils.custom_exception import CustomException

load_dotenv()

logger = get_logger(__name__)

def main():
    try:
        logger.info("Starting to build Yu-Gi-Oh! pipeline...")

        loader = YuGiOhDataLoader("data/yugioh_cards.csv" , "data/yugioh_processed.csv")
        processed_csv = loader.load_and_process()

        logger.info("Yu-Gi-Oh! card data loaded and processed...")

        vector_builder = VectorStoreBuilder(processed_csv)
        vector_builder.build_and_save_vectorstore()

        logger.info("Yu-Gi-Oh! vector store built successfully...")

        logger.info("Yu-Gi-Oh! pipeline built successfully!")
    except Exception as e:
            logger.error(f"Failed to execute Yu-Gi-Oh! pipeline {str(e)}")
            raise CustomException("Error during Yu-Gi-Oh! pipeline " , e)
    
if __name__=="__main__":
     main()

