import nltk 
import re   

def extract_feature(text, syn_list, reg=None):
    """
    Extracts specific features from text based on synonyms and optional regex pattern.
    
    Args:
        text (str): Input text to extract features from
        syn_list (list): List of synonyms to look for in the text
        reg (str, optional): Regular expression pattern to match after finding a synonym
        
    Returns:
        str/bool: Extracted feature if found, False otherwise
    """
    # Split text into sentences and tokenize
    sent = nltk.sent_tokenize(text.lower())
    words = [nltk.word_tokenize(s) for s in sent]
    
    # Get English stopwords and customize them
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # Keep 'from' and 'to' as they are important for location information
    simp_words = []
    for s in words:
        simp_words.append([x for x in s if not(x in (stop_words.union(set(['-', ':', '.'])) - set(['from', 'to'])))])
    
    # Compile regex pattern if provided
    if (reg):
        reg = re.compile(reg)
    
    # Search for features in the text
    for token in syn_list:
        for s in simp_words:
            # Split token into words for multi-word matching
            tok_split = token.split()
            if (tok_split[0] in s):
                cond = True
                index = s.index(tok_split[0])
                
                # Check if all words in the token match
                for w in tok_split[1:]:
                    index += 1
                    try:
                        if (w != s[index]):
                            cond = False
                            break
                    except:
                        break
                
                if (not cond):
                    continue
                
                # Extract the feature after the matched token
                try:
                    if (reg):
                        # If regex pattern is provided, match it
                        x = reg.match(s[index+1]).group()
                        if (x != ''):
                            return x
                        else:
                            continue
                    # If no regex pattern, return the next word
                    return s[index+1]
                except:
                    continue
    
    # Return False if no feature is found
    return False
