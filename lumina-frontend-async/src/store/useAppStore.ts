import { create } from 'zustand';
import {
  AppState,
  AppPhase,
  UploadedFile,
  ExtractedData,
  Query,
  QueryResult,
  GraphNode,
  DocumentAnalysis,
  FieldRecommendation
} from '../types';
import { PersonalityMode } from '../styles/designTokens';
import api from '../utils/api';

/**
 * Lumina App Store
 * Manages global state and phase transitions
 */

// Translator for backend error messages to user-friendly text
const translateErrorMessage = (message: any): string => {
  let errorString = "An unknown error occurred.";

  // --- THIS IS THE FIX ---
  // 1. Check if the message is already a string
  if (typeof message === 'string') {
    errorString = message;
  
  // 2. Check if it's an object with a 'message' or 'detail' key
  } else if (typeof message === 'object' && message !== null) {
    if (typeof message.message === 'string') {
      errorString = message.message;
    } else if (typeof message.detail === 'string') {
      errorString = message.detail;
    } else if (message.error && typeof message.error.message === 'string') {
      // This will catch your specific LiteLLM error object
      errorString = message.error.message;
    } else {
      // Fallback for other objects
      try {
        errorString = JSON.stringify(message);
      } catch (e) { /* ignore stringify error */ }
    }
  }
  // --- END FIX ---

  // Now, we are guaranteed that 'errorString' is a string
  // Check for specific error text from the backend
  if (errorString.includes("No appropriate index found")) {
    return "Your query was a bit too broad. No column was found and no new column was suggested. To find correlations or perform analysis, please be more specific about the columns you're interested in. For example, try asking: 'What is the correlation between price and user rating?'";
  }

  if (errorString.includes("overloaded") || errorString.includes("UNAVAILABLE")) {
    return "The AI model is currently overloaded or unavailable. Please try your query again in a moment.";
  }

  if (errorString.includes("No columns") && errorString.includes("queried")) {
    return "The specified columns could not be found. Please provide the column name and try again. If it's a new column, ask explicitly for it to be created.";
  }

  // A default fallback for any other error
  return errorString;
};


export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  phase: AppPhase.IDLE,
  personalityMode: 'neutral',
  sessionId: null,  // Track current database session ID
  uploadedFiles: [],
  documentAnalysis: null,  // New: stores AI recommendations
  extractedData: null,
  knowledgeGraph: [],
  graphData: null,  // Generated graph from query results
  isGeneratingGraph: false,  // Track graph generation state
  queries: [],
  currentQuery: null,
  currentResult: null,
  sidebarOpen: false,
  commandPaletteOpen: false,
  selectedNode: null,
  processingSteps: [],

  // Accessibility preferences
  accessibility: {
    fontSize: 'default', // 'default' | 'large'
    highContrast: false,
    lightMode: false,
  },

  // Error handling
  error: null,

  // Job status
  currentJobId: null,
  currentJobService: null,
  jobStatus: null,
  jobMessage: null,


  // Actions
  setAccessibilityOption: (option: 'fontSize' | 'highContrast' | 'lightMode', value: any) => {
    set(state => ({
      accessibility: {
        ...state.accessibility,
        [option]: value,
      },
    }));
  },

  setPhase: (phase: AppPhase) => {
    // Determine personality mode based on phase
    let personalityMode: PersonalityMode = 'neutral';

    switch (phase) {
      case AppPhase.IDLE:
        personalityMode = 'neutral';
        break;
      case AppPhase.UPLOADING:
      case AppPhase.ANALYZING:        // NEW: Analyzing documents
      case AppPhase.SCHEMA_REVIEW:    // NEW: User reviewing schema
      case AppPhase.PROCESSING:
        personalityMode = 'apollo'; // Methodical, strategic processing
        break;
      case AppPhase.READY:
      case AppPhase.QUERYING:
        personalityMode = 'hermes'; // Quick exploration and discovery
        break;
      case AppPhase.INSIGHT:
        personalityMode = 'neutral'; // Return to neutral after celebration
        break;
    }

    // Initialize processing steps based on phase
    let processingSteps = get().processingSteps;

    if (phase === AppPhase.ANALYZING) {
      processingSteps = [
        { id: 1, label: 'Extracting document excerpts', complete: false },
        { id: 2, label: 'Classifying documents', complete: false },
        { id: 3, label: 'Analyzing content and topics', complete: false },
        { id: 4, label: 'Generating schema recommendations', complete: false },
      ];
    } else if (phase === AppPhase.PROCESSING) {
      processingSteps = [
        { id: 1, label: 'Generating extraction schema', complete: false },
        { id: 2, label: 'Creating Pydantic models', complete: false },
        { id: 3, label: 'Extracting structured data', complete: false },
        { id: 4, label: 'Indexing for queries', complete: false },
      ];
    }

    set({ phase, personalityMode, processingSteps });
  },

  setProcessingStep: (stepId: number) => {
    set(state => ({
      processingSteps: state.processingSteps.map(step =>
        step.id <= stepId ? { ...step, complete: true } : step
      ),
    }));
  },

  uploadFiles: async (files: File[]) => {
    const fileIds = files.map((file, i) => `file-${Date.now()}-${i}`);

    // Initialize upload state
    const uploadedFiles: UploadedFile[] = files.map((file, i) => ({
      id: fileIds[i],
      name: file.name,
      size: file.size,
      status: 'uploading',
      progress: 0,
    }));

    set({
      uploadedFiles,
      phase: AppPhase.UPLOADING,
    });

    try {
      // Step 1: Upload files to backend
      const uploadResponse = await api.uploadFiles(files);

      // Extract and store session_id from response
      const sessionId = uploadResponse.session_id;

      // Update progress to 100% (upload complete) and store session_id
      set(state => ({
        sessionId,
        uploadedFiles: state.uploadedFiles.map(f => ({
          ...f,
          progress: 100,
          status: 'complete',
        })),
      }));

      // Step 2: Analyze documents and get AI recommendations
      // This automatically triggers after upload
      await get().analyzeDocuments();

    } catch (error) {
      console.error('Upload error:', error);
      set(state => ({
        uploadedFiles: state.uploadedFiles.map(f => ({
          ...f,
          status: 'error',
          error: error instanceof Error ? error.message : 'Upload failed',
        })),
        phase: AppPhase.IDLE,
      }));
    }
  },

  analyzeDocuments: async () => {
    get().setPhase(AppPhase.ANALYZING);

    try {
      // Get session_id from state
      const sessionId = get().sessionId;
      if (!sessionId) {
        throw new Error('No session ID available. Please upload files first.');
      }

      // Call /analyze endpoint (does classification + recommendation on backend)
      // This takes ~8-10 seconds
      // const analysisPromise = api.analyzeDocuments(sessionId);
      const analysisJob = await api.analyzeDocuments(sessionId);

      set({
        currentJobId: analysisJob.job_id,
        currentJobService: 'extraction',
        jobStatus: 'PENDING',
        jobMessage: 'Starting analysis...',
      })

      // Import the job tracker
      const { trackJob } = await import('../utils/jobManager');

      // Track analysis job with WebSocket
      const analysisResult = await trackJob(analysisJob.job_id, (update) => {
        console.log('📊 Analysis progress:', update);
        set({
          jobStatus: update.status,
          jobMessage: update.message,
        });

        // Update processing steps based on real-time messages
        if (update.message.includes('excerpts')) {
          get().setProcessingStep(1);
        } else if (update.message.includes('Classifying')) {
          get().setProcessingStep(2);
        } else if (update.message.includes('Analyzing content')) {
          get().setProcessingStep(3);
        } else if (update.message.includes('Storing results')) {
          get().setProcessingStep(4);
        }
      });

      console.log('✅ Analysis completed');

      // Job is done, Store the analysis result
      set({
        documentAnalysis: analysisResult,
        phase: AppPhase.SCHEMA_REVIEW, // Transition to review phase
        currentJobId: null,
        currentJobService: null,
      })
     
    } catch (error) {
      console.error('Analysis job error:', error);
      set({ 
        phase: AppPhase.IDLE,
        error: error instanceof Error ? error.message : "Analysis failed."
      });
    }
  },

  updateSchema: async (intention: string, fields: FieldRecommendation[]) => {
    try {
      // Get session_id from state
      const sessionId = get().sessionId;
      if (!sessionId) {
        throw new Error('No session ID available.');
      }

      // Update schema with user edits
      await api.updateSchema(sessionId, intention, fields);

      // Update local state
      set(state => ({
        documentAnalysis: state.documentAnalysis ? {
          ...state.documentAnalysis,
          recommendation: {
            ...state.documentAnalysis.recommendation,
            recommended_intention: intention,
            recommended_schema: fields,
          }
        } : null
      }));

    } catch (error) {
      console.error('Update schema error:', error);
      throw error;
    }
  },

  confirmAndExtract: async () => {
    get().setPhase(AppPhase.PROCESSING);

    try {
      const sessionId = get().sessionId;
      if (!sessionId) {
        throw new Error('No session ID available.');
      }

      const intention = get().documentAnalysis?.recommendation.recommended_intention ||
                       "Extract structured data from the uploaded documents";

      // Step 1: Start extraction job (returns job_id immediately)
      const extractResponse = await api.extractData(sessionId, intention);
      
      console.log('🚀 Extraction job started:', extractResponse.job_id);

      // Store job info and start tracking it
      set({
        currentJobId: extractResponse.job_id,
        currentJobService: 'extraction',
        jobStatus: 'PENDING',
        jobMessage: 'Starting extraction...',
      });

      // Import the job tracker
      const { trackJob } = await import('../utils/jobManager');

      // Track extraction job with WebSocket
      const extractionResult = await trackJob(extractResponse.job_id, (update) => {
        console.log('📊 Extraction progress:', update);
        set({
          jobStatus: update.status,
          jobMessage: update.message,
        });

        // Update processing steps based on message
        if (update.message.includes('schema')) {
          get().setProcessingStep(1);
        } else if (update.message.includes('Pydantic')) {
          get().setProcessingStep(2);
        } else if (update.message.includes('xtracting')) {
          get().setProcessingStep(3);
        }
      });

      console.log('✅ Extraction completed');

      // Step 2: Start indexing job
      const indexResponse = await api.indexData(sessionId);
      
      console.log('🚀 Indexing job started:', indexResponse.job_id);

      set({
        currentJobId: indexResponse.job_id,
        currentJobService: 'indexing',
        jobStatus: 'PENDING',
        jobMessage: 'Starting indexing...',
      });

      // Track indexing job
      await trackJob(indexResponse.job_id, (update) => {
        console.log('📊 Indexing progress:', update);
        set({
          jobStatus: update.status,
          jobMessage: update.message,
        });

        if (update.status === 'PROCESSING') {
          get().setProcessingStep(4);
        }
      });

      console.log('✅ Indexing completed');

      // Step 3: Fetch the final extracted data
      set({
        extractedData: {
          records: extractionResult.records || [],
          fields: Object.keys((extractionResult.records || [])[0] || {}).map(fieldName => ({
            name: fieldName,
            type: 'string', // Use a default type, since we only know the name
          })),
          metadata: {
            totalRecords: extractionResult.total_records || 0,
            source: get().uploadedFiles[0]?.name || 'unknown',
            extractedAt: new Date().toISOString(),
          }
        },
        phase: AppPhase.READY,
        currentJobId: null,
        currentJobService: null,
        jobStatus: null,
        jobMessage: null,
      });

    } catch (error) {
      console.error('Job error:', error);

      set({
        extractedData: {
          records: [],
          fields: [],
          metadata: {
            totalRecords: 0,
            source: get().uploadedFiles[0]?.name || 'unknown',
            extractedAt: new Date().toISOString(),
            errors: [{
              filename: 'System Error',
              error: error instanceof Error ? error.message : String(error)
            }],
          }
        },
        phase: AppPhase.READY,
        currentJobId: null,
        currentJobService: null,
        jobStatus: null,
        jobMessage: null,
      });
    }
  },

  // Added function for dynamically adjusting extracted columns
  updateExtractedData: (newRecords, newField) => {
    const currentData = get().extractedData;
    if (!currentData) return;

    console.log("🚀 Updating data table with new column:", newField.name);

    set({
      extractedData: {
        ...currentData,
        records: newRecords, // Replace old records with the new, complete list
        fields: [...currentData.fields, { name: newField.name, type: 'string' }], // Add the new field to the list of columns
      },
    });
  },

  fetchExtractedData: async () => {
    const sessionId = get().sessionId;
    if (!sessionId) {
      console.error("No session ID to fetch data for.");
      return;
    }

    console.log('🔄 Fetching (borna) updated extracted data...');
    // You could set a specific loading phase if you want
    set({ phase: AppPhase.QUERYING }); 

    try {
      // Call the function we just made in api.ts
      const newData = await api.getExtractedData(sessionId);
      console.log(">> NEW DATA IN fetchExtractedData:", newData);
      set({
        extractedData: newData,
        phase: AppPhase.READY, // Data is loaded, back to ready
        error: null,
      });
      console.log('✅ Extracted data state refreshed.');

    } catch (error: any) {
      console.error("Failed to refresh extracted data:", error);
      const friendlyErrorMessage = translateErrorMessage(error.response?.data?.detail || error.message);
      set({
        error: friendlyErrorMessage,
        phase: AppPhase.READY,
      });
    }
  },
  
  submitQuery: async (queryText: string) => {
    const query: Query = {
      id: `query-${Date.now()}`,
      text: queryText,
      timestamp: new Date(),
      status: 'processing',
    };

    set({
      currentQuery: query,
      phase: AppPhase.QUERYING,
      error: null,
      queries: [...get().queries, query],
    });

    try {
      const sessionId = get().sessionId;
      if (!sessionId) {
        throw new Error('No session ID available.');
      }

      const result = await api.queryData(sessionId, queryText, 5);

      console.log('📬 Received result from backend:', result);

      // Check if this is a dynamic extraction job
      if (result.result_type === 'function_job_start' && result.function_result?.new_job_id) {
        const newJobId = result.function_result.new_job_id;
        
        console.log('🆕 Dynamic extraction job started:', newJobId);

        // Store job info
        set({
          currentJobId: newJobId,
          currentJobService: 'dynamic_extraction',
          jobStatus: 'PENDING',
          jobMessage: result.answer,
        });

        // Import the job tracker
        const { trackJob } = await import('../utils/jobManager');

        // Track the dynamic extraction job
        const jobResult = await trackJob(newJobId, (update) => {
          console.log('📊 Dynamic extraction progress:', update);
          set({
            jobStatus: update.status,
            jobMessage: update.message,
          });
        });

        console.log('✅ Dynamic extraction completed:', jobResult);

        // Clear job tracking
        set({
          currentJobId: null,
          currentJobService: null,
          jobStatus: null,
          jobMessage: null,
        });

        // Re-run the original query to get the answer
        console.log('✅ Dynamic extraction completed:', jobResult);

        // Clear job tracking
        set({
          currentJobId: null,
          currentJobService: null,
          jobStatus: null,
          jobMessage: null,
        });

        // Re-run the original query to get the answer
        console.log('🔄 Re-running query to get final answer...');
        await get().fetchExtractedData(); // Refresh data before querying
        
        set({
          currentResult: {
            query: queryText,
            // Use the final message from the job result
            answer: jobResult.message || `I've successfully added the new column. The data grid is now updated.`,
            confidence: 1,
            sources: [],
            relevantRecords: [],
            result_type: 'function', // The function is now complete
            function_result: {
              ...(jobResult || {}),
              success: true 
            }, 
          },
          phase: AppPhase.INSIGHT,
          currentQuery: { ...query, status: 'complete' },
        });

        setTimeout(() => {
          if (get().phase === AppPhase.INSIGHT) {
            set({ phase: AppPhase.READY });
          }
        }, 4000);

        return;
      }


      // Handle regular query result
      if (
        result.result_type === 'function' &&
        result.function_result?.success &&
        result.function_result?.new_records &&
        result.function_result?.new_field
      ) {
        // TODO: gotta check this and perhaps later update it with await get().fetchExtractedData();
        get().updateExtractedData(
          result.function_result.new_records,
          result.function_result.new_field
        );
      }

      const mappedRecords = result.relevant_records 
        ? result.relevant_records.map(r => ({
            text: r.text,
            relevanceScore: r.relevanceScore,
            chunkId: r.chunkId
          }))
        : []; // Use an empty array for function calls
        
      const queryResult: QueryResult = {
        query: result.query,
        answer: result.answer,
        confidence: result.confidence,
        sources: result.sources,
        // relevantRecords: result.relevant_records.map(r => ({
        //   text: r.text,
        //   relevanceScore: r.relevanceScore,
        //   chunkId: r.chunkId
        // })),
        relevantRecords: mappedRecords,
        result_type: result.result_type,
        function_result: result.function_result,
      };

      set({
        currentResult: queryResult,
        phase: AppPhase.INSIGHT,
        currentQuery: { ...query, status: 'complete' },
      });

      setTimeout(() => {
        if (get().phase === AppPhase.INSIGHT) {
          set({ phase: AppPhase.READY });
        }
      }, 4000);

    } catch (error: any) {
      console.error('Caught API error from query:', error);

      const rawErrorMessage = error.response?.data?.detail || error.message || 'An unknown error occurred.';
      const friendlyErrorMessage = translateErrorMessage(rawErrorMessage);
      
      set({
        currentQuery: { ...query, status: 'error' },
        error: friendlyErrorMessage,
        phase: AppPhase.READY,
      });
    }
  },

  generateGraphFromQuery: async () => {
    const currentResult = get().currentResult;

    if (!currentResult || !currentResult.relevantRecords || currentResult.relevantRecords.length === 0) {
      console.error('No query results available to generate graph');
      return;
    }

    set({ isGeneratingGraph: true });

    try {
      const uniqueQueryId = crypto.randomUUID();

      console.log('🔍 Generating knowledge graph from query results...');

      // Call API to generate graph
      const graphResponse = await api.generateGraph(currentResult.relevantRecords, uniqueQueryId);

      console.log('✅ Graph generated successfully:', graphResponse);

      // Store graph data
      set({
        graphData: graphResponse,
        isGeneratingGraph: false,
      });

    } catch (error) {
      console.error('Graph generation error:', error);
      set({ isGeneratingGraph: false });
    }
  },

  selectNode: (nodeId: string | null) => {
    set({ selectedNode: nodeId });
  },

  toggleCommandPalette: () => {
    set(state => ({ commandPaletteOpen: !state.commandPaletteOpen }));
  },

  clearError: () => {
    set({ error: null });
  }
}));

/**
 * Hook to get current personality mode configuration
 */
export const usePersonalityMode = () => {
  const personalityMode = useAppStore(state => state.personalityMode);
  return personalityMode;
};

/**
 * Hook to check if system is processing
 */
export const useIsProcessing = () => {
  const phase = useAppStore(state => state.phase);
  return phase === AppPhase.UPLOADING || phase === AppPhase.PROCESSING || phase === AppPhase.QUERYING;
};
