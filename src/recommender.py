from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from src.prompt_template import get_yugioh_prompt

class YuGiOhRecommender:
    def __init__(self,retriever,api_key:str,model_name:str):
        self.llm = ChatGroq(api_key=api_key,model=model_name,temperature=0)
        self.retriever = retriever
        self.prompt = get_yugioh_prompt()

    def extract_card_name(self, query: str) -> str:
        """Extract potential card name from query"""
        # Common question patterns to remove
        question_patterns = [
            'what is the fusion material of',
            'what are the fusion materials of',
            'what does',
            'tell me about',
            'information about',
            'details about',
            'what is',
            'what are',
            'search for',
            'find',
            'cards related to',
            'what is the effect of',
            'fusion material for',
            'fusion materials for'
        ]

        # Clean up the query
        cleaned_query = query.lower().strip()

        # Remove question patterns
        for pattern in question_patterns:
            if cleaned_query.startswith(pattern):
                cleaned_query = cleaned_query[len(pattern):].strip()
                break

        # Remove question marks and other punctuation
        cleaned_query = cleaned_query.rstrip('?')

        # Extract first few words as potential card name (max 4 words)
        words = cleaned_query.split()
        if len(words) > 4:
            # Take first 4 words and check if it contains 'fusion material'
            if 'fusion' in words[:4] and 'material' in words[:6]:
                # Find words between 'fusion material' and question mark
                fusion_idx = cleaned_query.find('fusion material')
                if fusion_idx != -1:
                    after_fusion = cleaned_query[fusion_idx + len('fusion material'):].strip()
                    return after_fusion.rstrip('?')
            return ' '.join(words[:4])
        else:
            return cleaned_query

    def fallback_search(self, query: str):
        """Fallback search strategy for when primary search fails"""
        # Extract potential card name
        card_name = self.extract_card_name(query)

        # Enhanced fallback with query-type specific handling
        if 'atk' in query.lower() or 'attack' in query.lower():
            # For ATK queries, use power indicators and specific ATK ranges
            fallback_queries = [
                "3000+ ATK High Power Monster",  # High ATK cards
                "2500+ ATK Strong Monster",    # Strong ATK cards
                "4000+ ATK High Power Monster", # Very high ATK cards
                "2000+ ATK Moderate Power Monster", # Moderate ATK cards
                query,  # Original query
                "ATK 3000",  # Specific ATK values
                "ATK 2500",
                "ATK 4000"
            ]
        elif 'related to' in query.lower() or 'cards related' in query.lower():
            # For "related to" queries, search for mentions in descriptions
            fallback_queries = [
                f'mentions "{card_name}"',  # Cards that mention this card
                f'"{card_name}" in effect',  # Cards with effects mentioning this card
                f'supports "{card_name}"',  # Support cards for this card
                f'archetype {card_name}',  # Archetype cards
                f'{card_name} support',  # Support cards
                f'{card_name} synergy',  # Synergy cards
                f'Card Name: {card_name}',  # The card itself
                f'{card_name}',  # Direct mention
                f'{card_name} combo',  # Combo cards
                query  # Original query
            ]
        else:
            # Regular card name queries
            fallback_queries = [
                f"Card Name: {card_name} {card_name}",  # Double card name (highest priority)
                f"{card_name} {card_name}",  # Double name for emphasis
                f"Card Name: {card_name}",  # Card name format
                card_name,  # Just the card name
                f"Find {card_name}",  # Find format
                f"Search for {card_name}",  # Search format
                query,  # Original query (lowest priority)
                card_name.replace("dragon", "Dragon"),  # Capitalization fixes
                card_name.replace(" ", ""),  # No spaces
            ]

        prioritized_docs = []
        all_docs = []

        for fallback_query in fallback_queries:
            try:
                docs = self.retriever.invoke(fallback_query)
                if docs:
                    # Check if any doc contains the exact card name
                    for doc in docs:
                        if card_name.lower() in doc.page_content.lower() and doc not in prioritized_docs:
                            prioritized_docs.append(doc)

                    all_docs.extend(docs)
                    # If we found relevant docs, break early
                    if len(prioritized_docs) >= 3:
                        break
            except:
                continue

        # Combine prioritized docs with remaining docs
        # Remove duplicates while preserving order
        seen = set()
        unique_docs = []

        # Add prioritized docs first
        for doc in prioritized_docs:
            doc_id = id(doc.page_content)
            if doc_id not in seen:
                seen.add(doc_id)
                unique_docs.append(doc)

        # Add remaining docs
        for doc in all_docs:
            doc_id = id(doc.page_content)
            if doc_id not in seen:
                seen.add(doc_id)
                unique_docs.append(doc)

        return unique_docs[:15]  # Return more unique documents

    def get_recommendation(self,query:str):
        # Primary search
        docs = self.retriever.invoke(query)

        # Check if primary search found relevant results
        needs_fallback = False
        if not docs or len(docs) < 2:
            needs_fallback = True
        else:
            # Check if any document contains the extracted card name
            card_name = self.extract_card_name(query)
            found_card_name = False
            for doc in docs[:5]:  # Check first 5 documents
                if card_name.lower() in doc.page_content.lower():
                    found_card_name = True
                    break
            if not found_card_name:
                needs_fallback = True

            # Always use fallback for fusion material queries to ensure accuracy
            if 'fusion material' in query.lower():
                needs_fallback = True

            # Always use fallback for ATK-based queries to ensure accuracy
            elif 'atk' in query.lower() or 'attack' in query.lower():
                needs_fallback = True

        # If primary search fails or doesn't find relevant results, use fallback
        if needs_fallback:
            docs = self.fallback_search(query)

        # Combine context
        if not docs:
            context = "No specific card information found in the database."
        else:
            context = "\n\n".join([doc.page_content for doc in docs])

        # Create the prompt with context and question
        formatted_prompt = self.prompt.format(context=context, question=query)

        # Get response from LLM
        messages = [
            SystemMessage(content="You are an expert Yu-Gi-Oh! card analyst and strategist."),
            HumanMessage(content=formatted_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content
