import os
import glob
from typing import List, Dict

def load_and_chunk_documents(documents_dir: str) -> List[Dict[str, str]]:
    """
    Reads all .txt files from the specified directory and splits them into chunks
    based on paragraph breaks (\n\n).
    
    Returns a list of dictionaries containing the chunk content and its source file.
    """
    chunks = []
    
    # Use glob to find all .txt files in the directory
    search_pattern = os.path.join(documents_dir, "*.txt")
    txt_files = glob.glob(search_pattern)
    
    if not txt_files:
        print(f"No .txt files found in '{documents_dir}'.")
        return chunks
        
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split content by paragraph breaks (\n\n)
            # We strip whitespace and filter out empty chunks
            raw_chunks = [chunk.strip() for chunk in content.split('\n\n')]
            valid_chunks = [chunk for chunk in raw_chunks if chunk]
            
            for chunk in valid_chunks:
                chunks.append({
                    "source": os.path.basename(file_path),
                    "content": chunk
                })
                
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            
    return chunks

if __name__ == "__main__":
    # Define the path to the documents directory
    # Getting the absolute path to the root directory's documents folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    documents_folder = os.path.join(project_root, "documents")
    
    print(f"Loading documents from: {documents_folder}")
    
    # Run the function
    document_chunks = load_and_chunk_documents(documents_folder)
    
    print(f"\nTotal chunks generated: {len(document_chunks)}")
    print("-" * 40)
    
    # Print the first few chunks (e.g., up to 5)
    num_to_print = min(5, len(document_chunks))
    if num_to_print > 0:
        print(f"Printing the first {num_to_print} chunks:\n")
        for i in range(num_to_print):
            chunk_info = document_chunks[i]
            print(f"Chunk {i+1} [Source: {chunk_info['source']}]:")
            print(chunk_info['content'])
            print("-" * 40)
    else:
        print("No chunks were generated.")
