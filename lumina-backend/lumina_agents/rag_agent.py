"""
RAG (Retrieval-Augmented Generation) System Module

This module provides a complete RAG pipeline implementation including:
- Document chunking (markdown table rows)
- Text embedding via NVIDIA API
- GPU-accelerated retrieval with FAISS
- Reranking via NVIDIA API
- Response generation via Google Gemini

The RAGSystem class handles the entire workflow from document indexing
to query answering with citation support.
"""

import os
import re
import json
import datetime
from typing import List, Dict, Any, Optional, Tuple

import requests
from openai import OpenAI
import google.generativeai as genai
import faiss
import numpy as np


class RAGSystem:
    """
    A complete RAG pipeline implementation.
    
    This class provides methods for:
    - Chunking markdown documents into table rows
    - Embedding text using NVIDIA's embedding models
    - Indexing documents with FAISS for fast retrieval
    - Retrieving relevant documents based on semantic similarity
    - Reranking results using NVIDIA's reranker
    - Generating answers using Google Gemini
    
    The system supports saving and loading indexes for persistence.
    """

    # --- Constants ---
    DEFAULT_EMBED_MODEL = "nvidia/llama-3.2-nemoretriever-300m-embed-v1"
    DEFAULT_EMBED_URL = "https://integrate.api.nvidia.com/v1"

    DEFAULT_RERANKER_MODEL = "nvidia/llama-3.2-nemoretriever-500m-rerank-v2"
    DEFAULT_RERANKER_URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia/llama-3_2-nemoretriever-500m-rerank-v2/reranking"

    DEFAULT_GENERATOR_MODEL = 'gemini-2.5-flash'

    def __init__(
        self,
        embed_api_key: str,
        rerank_api_key: str,
        gemini_api_key: str,
        embed_model: str = DEFAULT_EMBED_MODEL,
        embed_base_url: str = DEFAULT_EMBED_URL,
        reranker_model: str = DEFAULT_RERANKER_MODEL,
        reranker_url: str = DEFAULT_RERANKER_URL,
        generator_model: str = DEFAULT_GENERATOR_MODEL,
        verbose: bool = False
    ):
        """
        Initialize the RAG pipeline system.

        Args:
            embed_api_key: NVIDIA API key for the embedding service
            rerank_api_key: NVIDIA API key for the reranking service
            gemini_api_key: Google API key for the Gemini generation service
            embed_model: The embedding model to use
            embed_base_url: The base URL for the embedding API
            reranker_model: The reranker model to use
            reranker_url: The API endpoint for the reranker
            generator_model: The Gemini model to use for generation
            verbose: If True, print detailed logging information
        """
        self.verbose = verbose

        # --- Device Setup ---
        self.device = None
        if self.verbose:
            print(f"RAGSystem initialized. Using NumPy.")

        # --- API Keys ---
        self.embed_api_key = embed_api_key
        self.rerank_api_key = rerank_api_key
        self.gemini_api_key = gemini_api_key

        # --- Model Configs ---
        self.embed_model = embed_model
        self.reranker_model = reranker_model
        self.reranker_url = reranker_url
        self.generator_model = generator_model

        # --- API Clients ---
        # 1. Embedding Client (OpenAI-compatible)
        self.embed_client = OpenAI(api_key=self.embed_api_key, base_url=embed_base_url)

        # 2. Reranker Client (Requests Session)
        self.reranker_session = requests.Session()
        self.reranker_session.headers.update({
            "Authorization": f"Bearer {self.rerank_api_key}",
            "Accept": "application/json",
        })

        # 3. Generator Client (Gemini)
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.generator_client = genai.GenerativeModel(self.generator_model)
            if self.verbose:
                print(f"Gemini client configured with model: {self.generator_model}")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Failed to configure Gemini client: {e}")
            self.generator_client = None

        # --- Data Storage ---
        self.document_embeddings: Optional[np.ndarray] = None
        self.chunks_metadata: List[Dict[str, Any]] = []

    def __del__(self):
        """Clean up resources, like the requests session."""
        if self.verbose:
            print("Closing RAGSystem resources...")
        if hasattr(self, 'reranker_session') and self.reranker_session:
            self.reranker_session.close()

    # --------------------------------------------------------------------------
    # 1. CHUNKING
    # --------------------------------------------------------------------------

    @staticmethod
    def chunk_by_table_row(markdown_content: str, min_char_len: int = 10) -> List[str]:
        """
        Split markdown content into table row strings.

        Identifies lines that look like markdown table rows (start and end with '|')
        and filters out the table separator line (e.g., |---|---|).

        Args:
            markdown_content: The full text content of the markdown file
            min_char_len: The minimum character length for a row to be included

        Returns:
            A list of strings, where each string is a single table row
        """
        # Regex to detect the separator line, e.g., |---| or |:---| or | --- |
        # This matches lines containing *only* pipe, hyphen, colon, and whitespace
        separator_regex = re.compile(r'^[|\s:-]+$')

        lines = markdown_content.split('\n')
        table_rows = []

        for line in lines:
            cleaned_line = line.strip()

            # Check if it looks like a table row (starts and ends with a pipe)
            if cleaned_line.startswith('|') and cleaned_line.endswith('|'):

                # Check if it's the separator line. If so, skip it.
                if separator_regex.match(cleaned_line):
                    continue

                # Only add non-empty rows with at least the minimum characters
                if len(cleaned_line) >= min_char_len:
                    table_rows.append(cleaned_line)

        return table_rows

    # --------------------------------------------------------------------------
    # 2. EMBEDDING & INDEXING (Internal Helpers + Public Method)
    # --------------------------------------------------------------------------

    def _embed_single_chunk(self, text: str, input_type: str = "query") -> Optional[List[float]]:
        """
        Generate embedding for a single text chunk.
        
        Args:
            text: The text to embed
            input_type: Either "query" or "passage"
            
        Returns:
            List of floats representing the embedding, or None on error
        """
        try:
            response = self.embed_client.embeddings.create(
                input=[text],
                model=self.embed_model,
                encoding_format="float",
                extra_body={"input_type": input_type, "truncate": "NONE"}
            )
            return response.data[0].embedding
        except Exception as e:
            if self.verbose:
                print(f"Error embedding chunk: {e}")
            return None

    def _embed_query(self, query: str) -> Optional[np.ndarray]:
        """
        Generate and tensorize embedding for a user query.
        
        Args:
            query: The query text to embed
            
        Returns:
            NumPy array of the embedding, or None on error
        """
        if self.verbose:
            print(f"Generating embedding for query: '{query[:100]}...'")
        embedding = self._embed_single_chunk(query, input_type="query")
        if embedding:
            if self.verbose:
                print(f"Successfully generated query embedding (dimension: {len(embedding)})")
            return np.array(embedding, dtype=np.float32)
        else:
            if self.verbose:
                print("Failed to generate query embedding")
            return None

    def _embed_multiple_chunks(
        self,
        chunks: List[str],
        input_type: str = "passage",
        batch_size: int = 10,
        show_progress: bool = True
    ) -> Optional[np.ndarray]:
        """
        Generate embeddings for multiple text chunks in batches.
        
        Args:
            chunks: List of text chunks to embed
            input_type: Either "query" or "passage"
            batch_size: Number of chunks to process in each batch
            show_progress: Whether to print progress information
            
        Returns:
            NumPy array of embeddings with shape (num_chunks, embedding_dim)
        """
        embeddings = []
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1

            if show_progress and self.verbose:
                print(f"Processing embedding batch {batch_num}/{total_batches}...")

            try:
                response = self.embed_client.embeddings.create(
                    input=batch,
                    model=self.embed_model,
                    encoding_format="float",
                    extra_body={"input_type": input_type, "truncate": "NONE"}
                )
                for data in response.data:
                    embeddings.append(data.embedding)
            except Exception as e:
                if self.verbose:
                    print(f"Error in batch {batch_num}: {e}. Skipping batch.")
                continue

        if not embeddings:
            raise ValueError("No embeddings were generated for the provided chunks.")

        # Convert to NumPy array
        embedding_array = np.array(embeddings, dtype=np.float32)
        return embedding_array

    def index_documents(
        self,
        chunks: List[str],
        *,
        base_metadata: Optional[Dict[str, Any]] = None,
        per_chunk_metadata: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 32,
        show_progress: bool = True
    ) -> None:
        """
        Index documents by generating and storing their embeddings.

        Args:
            chunks: List of text chunks to index
            base_metadata: Metadata applied to every chunk
            per_chunk_metadata: List of metadata dicts aligned with chunks
            batch_size: Batch size for embedding generation
            show_progress: Whether to show progress information
        """
        if self.verbose:
            print(f"Indexing {len(chunks)} documents...")

        # Generate embeddings
        self.document_embeddings = self._embed_multiple_chunks(
            chunks,
            input_type="passage",
            batch_size=batch_size,
            show_progress=show_progress
        )

        if self.document_embeddings is None:
            if self.verbose:
                print("Indexing failed as no embeddings were generated.")
            self.chunks_metadata = []
            return

        self.document_embeddings = self.document_embeddings.astype('float32')
        faiss.normalize_L2(self.document_embeddings)
        
        d = self.document_embeddings.shape[1]  # dimension
        self.faiss_index = faiss.IndexFlatIP(d)
        self.faiss_index.add(self.document_embeddings)
        
        # Store metadata
        self.chunks_metadata = []
        base_metadata = base_metadata or {}
        for i, text in enumerate(chunks):
            meta = {"id": i, "text": text}
            # apply base
            meta.update(base_metadata)
            # apply per-chunk
            if per_chunk_metadata and i < len(per_chunk_metadata):
                meta.update(per_chunk_metadata[i])
            self.chunks_metadata.append(meta)

        if self.verbose:
            print(f"Successfully indexed {len(self.chunks_metadata)} documents")
            print(f"Embeddings array shape: {self.document_embeddings.shape}")
            print(f"Embeddings stored in-memory (NumPy)")

    # --------------------------------------------------------------------------
    # 3. RETRIEVAL (Internal Helpers + Public Method)
    # --------------------------------------------------------------------------
    
    @staticmethod
    def _batch_calculate_similarities(
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Calculate cosine similarities between query and documents.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: Document embedding matrix
            normalize: Whether to normalize vectors
            
        Returns:
            1D array of cosine similarities with shape (num_docs,)
        """
        # ensure 1D
        if query_embedding.ndim > 1:
            query = query_embedding.reshape(-1)
        else:
            query = query_embedding

        docs = document_embeddings  # (N, D)

        if normalize:
            # normalize query
            q_norm = query / (np.linalg.norm(query) + 1e-12)
            # normalize docs row-wise
            d_norms = np.linalg.norm(docs, axis=1, keepdims=True) + 1e-12
            docs_norm = docs / d_norms
            sims = np.dot(docs_norm, q_norm)   # (N,)
        else:
            sims = np.dot(docs, query)

        return sims  # (N,)

    @staticmethod
    def _find_top_k_similar(
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray,
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find top-k most similar documents to the query.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: Document embedding matrix
            top_k: Number of top results to return
            threshold: Optional similarity threshold
            
        Returns:
            Tuple of (indices, scores) for top-k results
        """
        sims = RAGSystem._batch_calculate_similarities(query_embedding, document_embeddings)

        if threshold is not None:
            # mask out below threshold
            mask = sims >= threshold
            # to keep ordering, we can just set to -inf
            sims = np.where(mask, sims, -np.inf)

        top_k = min(top_k, sims.shape[0])

        # argpartition for top-k
        top_idx = np.argpartition(-sims, top_k - 1)[:top_k]   # unsorted indices
        # sort them by score descending
        top_idx = top_idx[np.argsort(-sims[top_idx])]

        top_scores = sims[top_idx]

        # if threshold, drop -inf
        if threshold is not None:
            valid = top_scores > -np.inf
            top_idx = top_idx[valid]
            top_scores = top_scores[valid]

        return top_idx, top_scores

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        threshold: Optional[float] = None,
        debug_json_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.

        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Optional similarity threshold
            debug_json_path: If provided, saves the raw retrieval results to this JSON file

        Returns:
            List of search results with scores and metadata
        """
        if self.document_embeddings is None:
            raise ValueError("No documents indexed. Call index_documents first.")

        # 1. Generate query embedding
        query_embedding = self._embed_query(query)
        if query_embedding is None:
            return []
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # 2. Find top-k similar documents
        distances, indices = self.faiss_index.search(query_embedding, top_k)

        # 3. Format results
        results: List[Dict[str, Any]] = []
        for idx, score in zip(indices[0], distances[0]):
            if idx == -1:
                continue

            chunk_meta = self.chunks_metadata[int(idx)]

            # start with the core fields
            result = {
                "chunk_id": chunk_meta["id"],
                "similarity_score": float(score),
                "text": chunk_meta["text"],
                "text_preview": chunk_meta["text"][:200] + "...",
            }

            # add extra metadata (like column_name, row_id, source_file, etc.)
            for k, v in chunk_meta.items():
                if k not in ("id", "text"):
                    result[k] = v

            results.append(result)

        if self.verbose:
            print(f"Retrieved {len(results)} chunks for query.")

        # 4. Save to debug JSON file if path is provided
        if debug_json_path:
            try:
                debug_data = {
                    'query': query,
                    'retrieved_at': datetime.datetime.now().isoformat(),
                    'retrieval_top_k': top_k,
                    'retrieval_threshold': threshold,
                    'results': results
                }
                with open(debug_json_path, 'w', encoding='utf-8') as f:
                    json.dump(debug_data, f, indent=2, ensure_ascii=False)
                if self.verbose:
                    print(f"Debug retrieval results saved to {debug_json_path}")
            except Exception as e:
                if self.verbose:
                    print(f"Warning: Failed to save debug JSON: {e}")

        return results

    # --------------------------------------------------------------------------
    # 4. RERANKING
    # --------------------------------------------------------------------------

    def rerank(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results using the NVIDIA Reranker API.

        Args:
            query: The original user query
            search_results: The list of dicts from the retrieve() method
            top_k: If provided, truncates the reranked list to this size

        Returns:
            A new list of search results, sorted by the new 'rerank_score'
        """
        if not search_results:
            if self.verbose:
                print("No search results to rerank.")
            return []

        if self.verbose:
            print(f"Reranking {len(search_results)} results for query: '{query[:50]}...'")

        # Format passages as required by the API
        passages_for_api = [{"text": res["text"]} for res in search_results]

        payload = {
            "model": self.reranker_model,
            "query": {"text": query},
            "passages": passages_for_api
        }

        try:
            response = self.reranker_session.post(self.reranker_url, json=payload)
            response.raise_for_status()  # Raise an error for bad responses
            response_body = response.json()

            rankings = response_body.get("rankings")
            if not rankings:
                if self.verbose:
                    print("Warning: Reranker response did not contain 'rankings'. Returning original results.")
                return search_results

            # Create a copy to avoid modifying the original list
            reranked_data = list(search_results)

            # Map rankings back to our original results
            for rank_data in rankings:
                original_index = rank_data.get("index")
                score = rank_data.get("logit")  # The reranker score

                if original_index is None or score is None:
                    continue

                if 0 <= original_index < len(reranked_data):
                    reranked_data[original_index]["rerank_score"] = score

            # Sort the list by the new rerank score, highest first
            reranked_data.sort(key=lambda x: x.get("rerank_score", float('-inf')), reverse=True)

            if self.verbose:
                print("Reranking complete.")

            # Truncate to top_k if specified
            if top_k is not None:
                reranked_data = reranked_data[:top_k]
                if self.verbose:
                    print(f"Returning reranked top {len(reranked_data)} results.")

            return reranked_data

        except requests.RequestException as e:
            if self.verbose:
                print(f"Error calling reranker API: {e}. Returning original (non-reranked) results.")
            return search_results
        except Exception as e:
            if self.verbose:
                print(f"Error processing reranker response: {e}. Returning original (non-reranked) results.")
            return search_results

    # --------------------------------------------------------------------------
    # 5. GENERATION
    # --------------------------------------------------------------------------

    def generate(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        top_k_context: int = 5
    ) -> str:
        """
        Generate a response using the Gemini API based on retrieved chunks.

        Args:
            query: The original user query
            retrieved_chunks: A list of dictionaries, assumed to be pre-sorted
            top_k_context: The number of top chunks to use as context

        Returns:
            A string containing the generated answer
        """
        if not self.generator_client:
            return "Error: Gemini client is not configured. Please check your API key."

        # 1. Extract text from the top-k chunks
        top_chunks = retrieved_chunks[:top_k_context]
        context_list = [chunk['text'] for chunk in top_chunks]

        if not context_list:
            return "Sorry, no relevant context was found to answer your query."

        # 2. Format the context for the prompt
        context_string = "\n\n---\n\n".join(context_list)

        # 3. Create the prompt
        prompt = f"""
        You are a helpful assistant. Please answer the following query based *only* on the provided context.
        If the answer cannot be found in the context, state that you cannot answer the question with the information given.

        QUERY:
        {query}

        CONTEXT:
        {context_string}

        ANSWER:
        """

        # 4. Generate the response
        if self.verbose:
            print(f"Generating response for query: '{query[:50]}...'")
        try:
            response = self.generator_client.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response from Gemini: {e}"

    # --------------------------------------------------------------------------
    # 6. INDEX PERSISTENCE
    # --------------------------------------------------------------------------

    def save_index(self, dir_path: str) -> None:
        """
        Save FAISS index, metadata, and embeddings to disk.
        
        Args:
            dir_path: Directory path where index files will be saved
        """
        if not hasattr(self, "faiss_index") or self.faiss_index is None:
            raise ValueError("No FAISS index to save. Did you call index_documents()?")

        os.makedirs(dir_path, exist_ok=True)

        # 1. save faiss index
        faiss.write_index(self.faiss_index, os.path.join(dir_path, "faiss.index"))

        # 2. save metadata
        with open(os.path.join(dir_path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(self.chunks_metadata, f, ensure_ascii=False, indent=2)

        # 3. save embeddings
        if self.document_embeddings is not None:
            np.save(os.path.join(dir_path, "embeddings.npy"), self.document_embeddings)

    def load_index(self, dir_path: str) -> None:
        """
        Load FAISS index, metadata, and embeddings from disk.
        
        Args:
            dir_path: Directory path where index files are stored
        """
        index_path = os.path.join(dir_path, "faiss.index")
        meta_path = os.path.join(dir_path, "metadata.json")
        emb_path = os.path.join(dir_path, "embeddings.npy")

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}")

        self.faiss_index = faiss.read_index(index_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.chunks_metadata = json.load(f)
        else:
            self.chunks_metadata = []

        if os.path.exists(emb_path):
            self.document_embeddings = np.load(emb_path)
        else:
            self.document_embeddings = None

    # --------------------------------------------------------------------------
    # 7. FULL PIPELINE
    # --------------------------------------------------------------------------

    def run_pipeline(
        self,
        query: str,
        retrieve_top_k: int = 20,
        rerank_top_k: int = 5,
        generate_context_top_k: int = 5,
        skip_generation: bool = False,
        debug_json_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the full RAG pipeline: Retrieve -> Rerank -> Generate.

        Args:
            query: The user's query
            retrieve_top_k: How many documents to fetch in the initial retrieval
            rerank_top_k: The number of documents to keep after reranking
            generate_context_top_k: The number of reranked documents to pass to the generator
            skip_generation: If True, skip the generation step
            debug_json_path: Path to save the raw retrieval (step 1) results

        Returns:
            A dictionary containing the query, final answer, and intermediate results
        """
        if self.verbose:
            print(f"\n{'='*60}\nRunning RAG pipeline for query: '{query}'\n{'='*60}")

        # --- 1. RETRIEVE ---
        if self.verbose:
            print(f"\n--- Step 1: Retrieving (Top {retrieve_top_k}) ---")
        try:
            retrieved_results = self.retrieve(
                query,
                top_k=retrieve_top_k,
                debug_json_path=debug_json_path
            )
        except Exception as e:
            if self.verbose:
                print(f"Error during retrieval: {e}")
            return {"query": query, "error": str(e)}

        if not retrieved_results:
            if self.verbose:
                print("No results found during retrieval. Pipeline stopped.")
            return {
                "query": query,
                "answer": "Sorry, I could not find any relevant information to answer your query.",
                "retrieved_results": [],
                "reranked_results": []
            }

        # --- 2. RERANK ---
        if self.verbose:
            print(f"\n--- Step 2: Reranking (Top {rerank_top_k}) ---")
        reranked_results = self.rerank(
            query,
            retrieved_results,
            top_k=rerank_top_k
        )

        # --- 3. GENERATE ---
        if skip_generation:
            if self.verbose:
                print("\nSkipping generation step as per configuration.")
            final_answer = "Generation step was skipped."
        else:
            if self.verbose:
                print(f"\n--- Step 3: Generating (Context {generate_context_top_k}) ---")
            final_answer = self.generate(
                query,
                reranked_results,  # Pass the reranked results
                top_k_context=generate_context_top_k
            )

        if self.verbose:
            print(f"\n{'='*60}\nPipeline Complete\n{'='*60}")

        # --- 4. RETURN ---
        return {
            "query": query,
            "answer": final_answer,
            "reranked_results": reranked_results,
            "retrieved_results": retrieved_results,  # Original, pre-reranked results
        }
