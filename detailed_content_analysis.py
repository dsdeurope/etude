#!/usr/bin/env python3
"""
Detailed Content Analysis for Bible API Fallback
Analyzes the actual content generated to understand similarity issues
"""

import requests
import json
import re
from difflib import SequenceMatcher

BACKEND_URL = "https://bible-study-app-6.preview.emergentagent.com/api"

def get_batch_content(passage):
    """Get content for a specific batch"""
    payload = {"passage": passage, "version": "LSG"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/generate-verse-by-verse", json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get('content', '')
        else:
            print(f"Error getting {passage}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception getting {passage}: {e}")
        return None

def extract_verse_sections(content, verse_num):
    """Extract specific sections for a verse"""
    # Find the verse section
    verse_pattern = f"\\*\\*VERSET {verse_num}\\*\\*"
    next_verse_pattern = f"\\*\\*VERSET {verse_num + 1}\\*\\*"
    
    verse_start = re.search(verse_pattern, content)
    if not verse_start:
        return None
    
    # Find where this verse ends (next verse starts or end of content)
    next_verse = re.search(next_verse_pattern, content)
    if next_verse:
        verse_content = content[verse_start.start():next_verse.start()]
    else:
        verse_content = content[verse_start.start():]
    
    # Extract each section
    sections = {}
    
    # CHAPITRE section
    chapitre_match = re.search(r'\*\*📚 CHAPITRE :\*\*(.*?)\*\*📜', verse_content, re.DOTALL)
    if chapitre_match:
        sections['chapitre'] = chapitre_match.group(1).strip()
    
    # CONTEXTE HISTORIQUE section
    contexte_match = re.search(r'\*\*📜 CONTEXTE HISTORIQUE :\*\*(.*?)\*\*✝️', verse_content, re.DOTALL)
    if contexte_match:
        sections['contexte'] = contexte_match.group(1).strip()
    
    # PARTIE THÉOLOGIQUE section
    theologie_match = re.search(r'\*\*✝️ PARTIE THÉOLOGIQUE :\*\*(.*?)(?=\*\*VERSET|\Z)', verse_content, re.DOTALL)
    if theologie_match:
        sections['theologie'] = theologie_match.group(1).strip()
    
    return sections

def calculate_similarity(text1, text2):
    """Calculate similarity between two texts"""
    return SequenceMatcher(None, text1, text2).ratio()

def analyze_content_uniqueness():
    """Analyze content uniqueness in detail"""
    print("🔍 DETAILED CONTENT UNIQUENESS ANALYSIS")
    print("="*60)
    
    # Get content for all 3 batches
    batches = [
        ("Batch 1", "Genèse 1:1-5", [1, 2, 3, 4, 5]),
        ("Batch 2", "Genèse 1:6-10", [6, 7, 8, 9, 10]),
        ("Batch 3", "Genèse 1:11-15", [11, 12, 13, 14, 15])
    ]
    
    batch_contents = {}
    
    # Fetch all content
    for batch_name, passage, verses in batches:
        print(f"\n📥 Fetching {batch_name}: {passage}")
        content = get_batch_content(passage)
        if content:
            batch_contents[batch_name] = content
            print(f"✅ Got {len(content)} characters")
        else:
            print(f"❌ Failed to get content")
            return False
    
    # Analyze each verse's sections across batches
    print(f"\n🔍 SECTION-BY-SECTION ANALYSIS")
    print("="*60)
    
    # Check if the same sections are being reused
    for section_name in ['chapitre', 'contexte', 'theologie']:
        print(f"\n📋 Analyzing {section_name.upper()} sections:")
        
        # Get all sections of this type from all batches
        all_sections = []
        for batch_name, passage, verses in batches:
            if batch_name in batch_contents:
                for verse_num in verses:
                    sections = extract_verse_sections(batch_contents[batch_name], verse_num)
                    if sections and section_name in sections:
                        section_text = sections[section_name]
                        all_sections.append((f"{batch_name} V{verse_num}", section_text))
        
        # Compare all sections
        if len(all_sections) >= 2:
            print(f"Found {len(all_sections)} {section_name} sections to compare")
            
            # Check for identical or very similar sections
            identical_count = 0
            very_similar_count = 0
            
            for i in range(len(all_sections)):
                for j in range(i + 1, len(all_sections)):
                    name1, text1 = all_sections[i]
                    name2, text2 = all_sections[j]
                    
                    similarity = calculate_similarity(text1, text2)
                    
                    if similarity >= 0.95:
                        identical_count += 1
                        print(f"  🚨 IDENTICAL ({similarity:.1%}): {name1} ↔ {name2}")
                        print(f"     Text: {text1[:100]}...")
                    elif similarity >= 0.8:
                        very_similar_count += 1
                        print(f"  ⚠️  VERY SIMILAR ({similarity:.1%}): {name1} ↔ {name2}")
            
            print(f"  📊 Summary: {identical_count} identical, {very_similar_count} very similar")
    
    # Show sample content from each batch
    print(f"\n📄 SAMPLE CONTENT FROM EACH BATCH")
    print("="*60)
    
    for batch_name in batch_contents:
        content = batch_contents[batch_name]
        print(f"\n{batch_name}:")
        
        # Extract first verse's CHAPITRE section as sample
        first_verse_sections = extract_verse_sections(content, batches[0][2][0] if batch_name == "Batch 1" else 
                                                     batches[1][2][0] if batch_name == "Batch 2" else batches[2][2][0])
        
        if first_verse_sections and 'chapitre' in first_verse_sections:
            print(f"CHAPITRE sample: {first_verse_sections['chapitre'][:200]}...")
        
        if first_verse_sections and 'contexte' in first_verse_sections:
            print(f"CONTEXTE sample: {first_verse_sections['contexte'][:200]}...")
    
    return True

if __name__ == "__main__":
    analyze_content_uniqueness()