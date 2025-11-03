import { PersonalityMode } from '../styles/designTokens';

/**
 * Application Phase System
 * Determines UI state and personality mode
 */
export enum AppPhase {
  IDLE = 'idle',                    // Waiting for user, EVE neutral
  UPLOADING = 'uploading',          // Files being uploaded
  ANALYZING = 'analyzing',          // Analyzing documents and recommending schema, Apollo mode
  SCHEMA_REVIEW = 'schema_review',  // User reviewing and editing AI-recommended schema, Apollo mode
  PROCESSING = 'processing',        // Backend extracting data, Apollo mode
  READY = 'ready',                  // Data ready for exploration, Hermes mode
  QUERYING = 'querying',            // Active query in progress, Hermes intensified
  INSIGHT = 'insight',              // Insight bloom, celebration state
}

/**
 * Job Status Types for Async Operations
 */
export type JobStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface JobResponse {
  job_id: string;
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  service: string;
  status: JobStatus;
  message: string;
  timestamp: number;
  result?: any;
}

/**
 * WebSocket Job Update Message
 */
export interface JobUpdate {
  job_id: string;
  status: JobStatus;
  message: string;
  timestamp: number;
  result?: any;
}

/**
 * File Upload State
 */
export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  error?: string;
}

/**
 * Extracted Data Structure
 */
export interface ExtractedData {
  records: Record<string, any>[];
  fields: DataField[];
  metadata: {
    totalRecords: number;
    source: string;
    extractedAt: string;
    errors?: Array<{
      filename: string;
      error: string;
    }>;
  };
}

export interface DataField {
  name: string;
  type: string;
  description?: string;
  unit?: string;
}

/**
 * Document Analysis Types
 */
export interface DocumentClassification {
  document_name: string;
  document_type: string;
  domain: string;
  key_topics: string[];
  data_types_present: string[];
  confidence: number;
}

export interface FieldRecommendation {
  field_name: string;
  description: string;
  data_type: string;
  unit?: string;
  example: string;
  validation_rules?: string;
}

export interface IntentionRecommendation {
  recommended_intention: string;
  reasoning: string;
  document_summary: string;
  recommended_schema: FieldRecommendation[];
  confidence: number;
}

export interface DocumentAnalysis {
  classifications: DocumentClassification[];
  recommendation: IntentionRecommendation;
}

/**
 * Query and Response
 */
export interface Query {
  id: string;
  text: string;
  timestamp: Date;
  status: 'pending' | 'processing' | 'complete' | 'error';
}

export interface QueryResult {
  query: string;
  answer: string;
  confidence: number;
  sources: Source[];
  relevantRecords: RelevantRecord[];
  result_type?: 'rag' | 'function' | 'function_job_start';  // ADD function_job_start
  function_result?: {
    success: boolean;
    message: string;
    filepath?: string;
    record_count?: number;
    new_field?: Field;
    new_records?: Record<string, any>[];
    records_updated?: number;
    sample_values?: any[];
    new_job_id?: string;  // ADD THIS - for dynamic extraction jobs
  };
  rowId?: string; // Optional row identifier for UI purposes
}

export interface Source {
  documentId: string;
  documentName: string;
  page?: number;
  excerpt: string;
}

export interface RelevantRecord {
  text: string;
  relevanceScore: number;
  chunkId: number;
}

/**
 * Knowledge Graph Node
 */
export interface GraphNode {
  id: string;
  label: string;
  type: 'entity' | 'cluster' | 'insight' | string;
  size: number;
  position: { x: number; y: number };
  connections: string[]; // IDs of connected nodes
  metadata: Record<string, any>;
  properties?: Record<string, any>;
}

/**
 * Knowledge Graph Relationship
 */
export interface GraphRelationship {
  source: GraphNode;
  target: GraphNode;
  type: string;
  properties?: Record<string, any>;
}

/**
 * Graph Generation Response
 */
export interface GraphGenerationResponse {
  success: boolean;
  message: string;
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}

/**
 * Processing Step for progress visualization
 */
export interface ProcessingStep {
  id: number;
  label: string;
  complete: boolean;
}

/**
 * Accessibility Preferences
 */
export interface AccessibilityPreferences {
  fontSize: 'default' | 'large';
  highContrast: boolean;
  lightMode: boolean;
}

/**
 * Global App State
 */
export interface AppState {
  // Phase management
  phase: AppPhase;
  personalityMode: PersonalityMode;

  // Session tracking
  sessionId: number | null;  // Current database session ID

  // Data
  uploadedFiles: UploadedFile[];
  documentAnalysis: DocumentAnalysis | null;  // New: AI-recommended schema
  extractedData: ExtractedData | null;
  knowledgeGraph: GraphNode[];
  graphData: GraphGenerationResponse | null;  // Generated graph from query results
  isGeneratingGraph: boolean;  // Track graph generation state

  // Query history
  queries: Query[];
  currentQuery: Query | null;
  currentResult: QueryResult | null;

  // UI state
  sidebarOpen: boolean;
  commandPaletteOpen: boolean;
  selectedNode: string | null;
  processingSteps: ProcessingStep[];  // New: Track progress through analysis/extraction

  // Accessibility preferences
  accessibility: AccessibilityPreferences;

  // Error handling
  error: string | null;

  // Async job tracking
  currentJobId: string | null;
  currentJobService: 'extraction' | 'indexing' | 'dynamic_extraction' | null;
  jobStatus: JobStatus | null;
  jobMessage: string | null;

  // Actions
  setAccessibilityOption: (option: 'fontSize' | 'highContrast' | 'lightMode', value: any) => void;
  setPhase: (phase: AppPhase) => void;
  setProcessingStep: (stepId: number) => void;  // New: Update progress
  uploadFiles: (files: File[]) => Promise<void>;
  analyzeDocuments: () => Promise<void>;  // New: Analyze documents
  updateSchema: (intention: string, fields: FieldRecommendation[]) => Promise<void>;  // New: Update schema
  confirmAndExtract: () => Promise<void>;  // New: Proceed with extraction
  submitQuery: (query: string) => Promise<void>;
  generateGraphFromQuery: () => Promise<void>;  // New: Generate graph from current query results
  selectNode: (nodeId: string | null) => void;
  toggleCommandPalette: () => void;
  updateExtractedData: (newRecords: any[], newField: { name: string }) => void;
  fetchExtractedData: () => Promise<void>;
}

/**
 * Backend API Response Types
 */
export interface BackendUploadResponse {
  success: boolean;
  message: string;
  fileIds: string[];
  session_id: number;  // Session ID from database
}

export interface BackendExtractionResponse {
  success: boolean;
  records: Record<string, any>[];
  total_records: number;
  errors?: Array<{
    filename: string;
    error: string;
  }>;
}

export interface Field {
  name: string;
  type: string;
  description: string;
}

export interface FunctionResult {
  success: boolean;
  message: string;
  // Fields for CSV Export
  filepath?: string;
  record_count?: number;
  // Fields for Dynamic Extraction
  new_records?: Record<string, any>[];
  new_field?: Field;
  records_updated?: number;
  sample_values?: any[];
  // New Job ID for async extraction
  new_job_id?: string;
}

export interface BackendQueryResponse {
  query: string;
  answer: string;
  confidence: number;
  sources: Source[]; // Assuming you have a Source type
  relevant_records: Array<{
    text: string;
    relevanceScore: number;
    chunkId: number;
  }>;
  result_type?: 'rag' | 'function' | 'function_job_start' | undefined;
  function_result?: FunctionResult;
}
