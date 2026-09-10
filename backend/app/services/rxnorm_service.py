"""
Drug Database Service - Fetches medications from RxNorm API (NIH)
with local caching to avoid repeated API calls.

RxNorm is the official US drug nomenclature system maintained by the NIH.
Free API: https://rxnav.nlm.nih.gov/APIs.html
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import httpx
from app.utils.logger import logger

# Local cache file
CACHE_FILE = Path("app/data/rxnorm_cache.json")
CACHE_DURATION_HOURS = 24  # Refresh cache every 24 hours

class RxNormService:
    """Fetch medication data from RxNorm API with local caching"""
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    def __init__(self):
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load medication cache from disk"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    if self._is_cache_valid(data.get('timestamp')):
                        logger.info(f"Loaded drug cache with {len(data.get('drugs', {}))} entries")
                        return data.get('drugs', {})
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        return {}
    
    def _is_cache_valid(self, timestamp: str) -> bool:
        """Check if cache is still valid (less than CACHE_DURATION_HOURS old)"""
        try:
            cached_time = datetime.fromisoformat(timestamp)
            return datetime.now() - cached_time < timedelta(hours=CACHE_DURATION_HOURS)
        except:
            return False
    
    def _save_cache(self):
        """Save current cache to disk"""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'drugs': self.cache
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    async def search_drug(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a drug by name in RxNorm API.
        Returns drug info if found, None otherwise.
        """
        drug_name_lower = drug_name.lower().strip()
        
        # Check cache first
        if drug_name_lower in self.cache:
            logger.debug(f"Drug '{drug_name}' found in cache")
            return self.cache[drug_name_lower]
        
        # Query RxNorm API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/drugs.json",
                    params={"name": drug_name}
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract drug info from response
                if 'drugGroup' in data and 'conceptGroup' in data['drugGroup']:
                    for group in data['drugGroup']['conceptGroup']:
                        if 'concept' in group:
                            for concept in group['concept']:
                                drug_info = self._parse_rxnorm_response(concept, drug_name)
                                if drug_info:
                                    # Cache it
                                    self.cache[drug_name_lower] = drug_info
                                    self._save_cache()
                                    logger.info(f"Fetched '{drug_name}' from RxNorm API")
                                    return drug_info
        except httpx.TimeoutException:
            logger.warning(f"RxNorm API timeout for '{drug_name}'")
        except httpx.HTTPError as e:
            logger.warning(f"RxNorm API error for '{drug_name}': {e}")
        except Exception as e:
            logger.warning(f"Error querying RxNorm for '{drug_name}': {e}")
        
        return None
    
    def _parse_rxnorm_response(self, concept: Dict[str, Any], search_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse RxNorm API response into our medication format.
        RxNorm returns: {"rxcui": "...", "name": "...", "tty": "..."}
        """
        try:
            rxcui = concept.get('rxcui', '')
            name = concept.get('name', '')
            tty = concept.get('tty', '')  # Term Type (e.g., "SCD" = Semantic Clinical Drug)
            
            if not name:
                return None
            
            # Prefer branded or clinical names
            if tty not in ['SCD', 'SBD', 'GPCK']:  # Skip pure chemical names
                if tty not in ['IN', 'BN', 'SY']:  # Prefer not synonyms
                    return None
            
            return {
                "generic_name": name,
                "brand_name": name,
                "rxcui": rxcui,
                "class": "Medication",
                "uses": "See pharmacist or FDA database for detailed information",
                "how_to_take": "Follow doctor's instructions on prescription label",
                "side_effects": ["Consult pharmacist for detailed information"],
                "warnings": ["Follow all instructions on prescription label"],
                "serious_symptoms": ["Seek immediate medical attention if symptoms occur"],
                "allergies": ["Inform doctor of all known drug allergies"],
                "mechanism": "See FDA or RxNorm database for pharmacological details",
                "source": "RxNorm (NIH)",
                "rxcui": rxcui
            }
        except Exception as e:
            logger.debug(f"Could not parse RxNorm response: {e}")
            return None
    
    def get_cached_drugs(self) -> Dict[str, Any]:
        """Get all cached drugs"""
        return self.cache.copy()

# Global service instance
rxnorm_service = RxNormService()

async def lookup_drug_online(drug_name: str) -> Optional[Dict[str, Any]]:
    """Wrapper function for looking up drugs from RxNorm API"""
    return await rxnorm_service.search_drug(drug_name)
