import axios from 'axios';
import {
  BackendUploadResponse,
  BackendQueryResponse,
  FieldRecommendation,
  ExtractedData,
} from '../types';

/**
 * API Client for Lumina Backend
 * Communicates with the FastAPI backend (api.py)
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for long-running operations
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload files to the server using the 3-step microservices flow
 * Step 1: Initiate upload session
 * Step 2: Upload each file
 * Step 3: Finalize the session
 */
export async function uploadFiles(files: File[]): Promise<BackendUploadResponse> {
  try {
    // Step 1: Initiate upload session with filenames
    console.log('📤 Step 1: Initiating upload session...');
    const filenames = files.map(file => file.name);
    
    const initiateResponse = await apiClient.post('/uploads/initiate', {
      filenames: filenames,
    });

    const sessionId = initiateResponse.data.session_id;
    console.log(`✅ Session created: ${sessionId}`);

    // Step 2: Upload each file individually
    console.log('📤 Step 2: Uploading files...');
    for (const file of files) {
      const formData = new FormData();
      formData.append('session_id', sessionId.toString());
      formData.append('file', file);

      const uploadResponse = await apiClient.post('/uploads/file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log(`✅ Uploaded: ${file.name} - Status: ${uploadResponse.data.status}`);
    }

    // Step 3: Finalize the upload session
    console.log('📤 Step 3: Finalizing upload session...');
    const finalizeResponse = await apiClient.post(`/uploads/finalize/${sessionId}`);
    
    console.log(`✅ Upload complete: ${finalizeResponse.data.message}`);

    // Return the response in the expected format
    return {
      success: true,
      message: finalizeResponse.data.message,
      fileIds: files.map((_, i) => `file-${sessionId}-${i}`),
      session_id: sessionId,
    };

  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}

/**
 * Analyze uploaded documents and get AI recommendations
 * NEW: First step after upload
 */
export async function analyzeDocuments(sessionId: number): Promise<{ job_id: string; message: string }> {
  try {
    const response = await apiClient.post('/orchestrate/analyze', {
      session_id: sessionId
    });
    // The backend now returns a job ID, just like the extract and index endpoints.
    return response.data;
  } catch (error) {
    console.error('Analysis error:', error);
    throw error;
  }
}

/**
 * Update schema with user edits
 * NEW: After user reviews and edits the AI recommendations
 */
export async function updateSchema(
  sessionId: number,
  intention: string,
  fields: FieldRecommendation[]
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await apiClient.post('/orchestrate/update-schema', {
      session_id: sessionId,
      intention,
      fields,
    });
    return response.data;
  } catch (error) {
    console.error('Update schema error:', error);
    throw error;
  }
}

/**
 * Extract data from uploaded files
 * Now works with /analyze + /update-schema for better results
 */
export async function extractData(
  sessionId: number,
  intention: string
): Promise<{ job_id: string; message: string }> {
  try {
    const response = await apiClient.post('/orchestrate/extract', {
      session_id: sessionId,
      intention,
    });

    // Response now contains { job_id, message }
    return response.data;
  } catch (error) {
    console.error('Extraction error:', error);
    throw error;
  }
}

/**
 * Query the indexed data using RAG
 */
export async function queryData(
  sessionId: number,
  query: string,
  numResults: number = 5
): Promise<BackendQueryResponse> {
  try {
    const response = await apiClient.post('/orchestrate/query', {
      session_id: sessionId,
      query,
      num_results: numResults,
    });

    return response.data;
  } catch (error) {
    console.error('Query error:', error);
    throw error;
  }
}

/**
 * Index data for RAG queries
 */
export async function indexData(
  sessionId: number
): Promise<{ job_id: string; message: string }> {
  try {
    const response = await apiClient.post('/orchestrate/index', {
      session_id: sessionId,
    });

    // Response now contains { job_id, message }
    return response.data;
  } catch (error) {
    console.error('Index error:', error);
    throw error;
  }
}

/**
 * Get job status (for polling fallback)
 */
export async function getJobStatus(jobId: string): Promise<any> {
  try {
    const response = await apiClient.get(`/jobs/${jobId}/status`);
    return response.data;
  } catch (error) {
    console.error('Job status error:', error);
    throw error;
  }
}

/**
 * Export extracted data
 */
export async function exportData(format: 'json' | 'csv'): Promise<Blob> {
  try {
    const response = await apiClient.get(`/export?format=${format}`, {
      responseType: 'blob',
    });

    return response.data;
  } catch (error) {
    console.error('Export error:', error);
    throw error;
  }
}

/**
 * Fetches the complete extracted data for the current session.
 */
export const getExtractedData = async (sessionId: string | number): Promise<ExtractedData> => {
  try {
    // NOTE: You might need to adjust this endpoint to match your backend!
    // This endpoint should return the full { records: [], fields: [], ... } object.
    const response = await apiClient.get<ExtractedData>(`/session/${sessionId}/data`);
    console.log('📬 Received extracted data (utils/api.py - L218):', response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching extracted data:", error);
    throw error;
  }
};

/**
 * Generate knowledge graph from query results
 */
export async function generateGraph(
  relevantRecords: any[],
  queryId: string
): Promise<any> {
  try {
    // 1. Create the payload object
    const payload = {
      relevant_records: relevantRecords,
      query_id: queryId,
    };

    // 2. Log it to the console
    console.log("--- Sending to /generate-graph ---");
    console.log(JSON.stringify(payload, null, 2));
    // --- END ---
    
    const response = await apiClient.post('/generate-graph', payload);
    return response.data;
  } catch (error) {
    console.error('Graph generation error:', error);
    throw error;
  }
}

/**
 * Health check endpoint
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}

export default {
  uploadFiles,
  analyzeDocuments,
  updateSchema,
  extractData,
  queryData,
  getExtractedData,
  indexData,
  exportData,
  generateGraph,
  healthCheck,
};
