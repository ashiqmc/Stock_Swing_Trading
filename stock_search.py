import streamlit as st
import requests
import json

def search_stocks(query):
    """
    Search for stocks using Yahoo Finance API
    
    Args:
        query (str): The search query string
    
    Returns:
        list: List of dictionaries containing stock information (symbol, name, exchange)
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        
        if 'quotes' not in data or not data['quotes']:
            return []
        
        results = []
        for quote in data['quotes']:
            if 'symbol' in quote and 'shortname' in quote:
                results.append({
                    'symbol': quote['symbol'],
                    'name': quote['shortname'],
                    'exchange': quote.get('exchange', 'Unknown')
                })
        return results
    except Exception as e:
        st.error(f"Error searching for stocks: {e}")
        return []