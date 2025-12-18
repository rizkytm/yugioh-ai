import pandas as pd
import numpy as np

class YuGiOhDataLoader:
    def __init__(self, original_csv: str, processed_csv: str):
        self.original_csv = original_csv
        self.processed_csv = processed_csv

    def clean_card_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize Yu-Gi-Oh! card data"""
        # Replace 'None' strings with proper empty values
        df = df.replace('None', np.nan)
        df = df.replace('', np.nan)

        # Convert numeric fields to proper numeric types
        numeric_fields = ['atk', 'def', 'level', 'rank', 'linkval']
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors='coerce')

        # Fill missing numeric values with 0
        for field in numeric_fields:
            df[field] = df[field].fillna(0)

        # Clean text fields
        text_fields = ['name', 'type', 'desc', 'race', 'attribute', 'archetype']
        for field in text_fields:
            df[field] = df[field].fillna('')
            df[field] = df[field].astype(str).str.strip()

        return df

    def is_monster_card(self, card_type: str) -> bool:
        """Check if a card is a monster type"""
        monster_keywords = ['Monster', 'Fusion', 'Synchro', 'Xyz', 'Link', 'Pendulum', 'Ritual', 'Spirit', 'Toon', 'Union']
        return any(keyword in card_type for keyword in monster_keywords)

    def create_combined_info(self, row: pd.Series) -> str:
        """Create combined information string for semantic search"""
        name = row['name'] if pd.notna(row['name']) else ''
        card_type = row['type'] if pd.notna(row['type']) else ''
        desc = row['desc'] if pd.notna(row['desc']) else ''
        race = row['race'] if pd.notna(row['race']) else ''
        attribute = row['attribute'] if pd.notna(row['attribute']) else ''
        archetype = row['archetype'] if pd.notna(row['archetype']) else ''

        # Build base info
        info_parts = [f"Card: {name}", f"Type: {card_type}"]

        # Add race if available
        if race:
            info_parts.append(f"Race: {race}")

        # Add attribute if available (mainly for monsters)
        if attribute:
            info_parts.append(f"Attribute: {attribute}")

        # Handle monster-specific fields
        if self.is_monster_card(card_type):
            atk = row['atk'] if pd.notna(row['atk']) and row['atk'] != 0 else ''
            def_ = row['def'] if pd.notna(row['def']) and row['def'] != 0 else ''
            level = row['level'] if pd.notna(row['level']) and row['level'] != 0 else ''
            rank = row['rank'] if pd.notna(row['rank']) and row['rank'] != 0 else ''
            linkval = row['linkval'] if pd.notna(row['linkval']) and row['linkval'] != 0 else ''

            if atk:
                info_parts.append(f"ATK: {int(atk)}")
            if def_:
                info_parts.append(f"DEF: {int(def_)}")
            if level:
                info_parts.append(f"Level: {int(level)}")
            elif rank:
                info_parts.append(f"Rank: {int(rank)}")
            elif linkval:
                info_parts.append(f"Link: {int(linkval)}")

        # Add archetype if available
        if archetype:
            info_parts.append(f"Archetype: {archetype}")

        # Add effect description (most important for search)
        if desc:
            info_parts.append(f"Effect: {desc}")

        return ' '.join(info_parts)

    def load_and_process(self):
        """Load Yu-Gi-Oh! card data and create processed search content"""
        try:
            # Load the Yu-Gi-Oh! CSV
            df = pd.read_csv(self.original_csv, encoding='utf-8')
        except Exception as e:
            raise ValueError(f"Error loading CSV file {self.original_csv}: {e}")

        # Check for required columns
        required_cols = {'name', 'type', 'desc'}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns in Yu-Gi-Oh! CSV: {missing}")

        # Clean the data
        df = self.clean_card_data(df)

        # Create combined_info for semantic search
        df['combined_info'] = df.apply(self.create_combined_info, axis=1)

        # Remove rows with empty combined_info
        df = df[df['combined_info'].str.len() > 20]  # Basic length filter

        # Save only the combined_info column for the vector store
        df[['combined_info']].to_csv(self.processed_csv, index=False, encoding='utf-8')

        print(f"Processed {len(df)} Yu-Gi-Oh! cards")
        print(f"Sample combined_info: {df.iloc[0]['combined_info'][:200]}...")

        return self.processed_csv
