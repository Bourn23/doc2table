import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '../store/useAppStore';
import { colors, typography } from '../styles/designTokens';
import { FieldRecommendation } from '../types';
import { Plus, X, Info, Check, FileText, Brain, Sparkles } from 'lucide-react';

/**
 * Generic Info Popup Component for DRY code
 */
const InfoPopup: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <motion.div
    initial={{ opacity: 0, y: -10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="absolute top-full left-0 mt-2 w-72 p-4 rounded-lg border shadow-lg z-10"
    style={{
      backgroundColor: colors.midnight.light,
      borderColor: `${colors.apollo.primary}50`,
    }}
  >
    <h4 className="font-semibold mb-2" style={{ color: colors.text.primary }}>
      {title}
    </h4>
    <div className="text-sm space-y-2" style={{ color: colors.text.secondary }}>
      {children}
    </div>
  </motion.div>
);


/**
 * Schema Editor View
 *
 * Allows users to review and edit AI-recommended extraction schema before extraction.
 * Shows document classifications and lets users modify intention and fields.
 */

/**
 * Schema Editor View
 *
 * Allows users to review and edit AI-recommended extraction schema before extraction.
 * Shows document classifications and lets users modify intention and fields.
 */
export const SchemaEditorView: React.FC = () => {
  const { documentAnalysis, updateSchema, confirmAndExtract } = useAppStore();

  const [intention, setIntention] = useState('');
  const [fields, setFields] = useState<FieldRecommendation[]>([]);
  const [isEditing, setIsEditing] = useState(false);

  // Info pop-up states
  const [showSchemaInfo, setShowSchemaInfo] = useState(false);
  const [showIntentionInfo, setShowIntentionInfo] = useState(false);
  const [activeInfoPopup, setActiveInfoPopup] = useState<string | null>(null);

  // Initialize from document analysis
  useEffect(() => {
    if (documentAnalysis) {
      setIntention(documentAnalysis.recommendation.recommended_intention);
      setFields([...documentAnalysis.recommendation.recommended_schema]);
    }
  }, [documentAnalysis]);

  if (!documentAnalysis) return null;

  const { classifications, recommendation } = documentAnalysis;

  // Handle field editing
  const updateField = (index: number, updates: Partial<FieldRecommendation>) => {
    const newFields = [...fields];
    newFields[index] = { ...newFields[index], ...updates };
    setFields(newFields);
    setIsEditing(true);
  };

  const removeField = (index: number) => {
    setFields(fields.filter((_, i) => i !== index));
    setIsEditing(true);
  };

  const addField = () => {
    setFields([
      ...fields,
      {
        field_name: '',
        description: '',
        data_type: 'string',
        example: '',
        unit: undefined,
        validation_rules: undefined,
      }
    ]);
    setIsEditing(true);
  };

  const handleSaveChanges = async () => {
    try {
      await updateSchema(intention, fields);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save schema:', error);
    }
  };

  const handleConfirm = async () => {
    if (isEditing) {
      await handleSaveChanges();
    }
    await confirmAndExtract();
  };

  const handleInfoToggle = (popupKey: string) => {
    setActiveInfoPopup(prev => (prev === popupKey ? null : popupKey));
  };

return (
    <div className="w-full h-full flex flex-col items-center justify-center p-8 overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-5xl w-full space-y-8"
      >
        {/* Header */}
        <div className="text-center space-y-2">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
            style={{ backgroundColor: `${colors.apollo.primary}20` }}
          >
            <Brain size={32} style={{ color: colors.apollo.primary }} />
          </motion.div>

          <h1 style={{ ...typography.heading, color: colors.text.primary }}>
            Summary and AI Recommendations
          </h1>

          <p style={{ ...typography.body, color: colors.text.secondary, maxWidth: '600px', margin: '0 auto' }}>
            {recommendation.reasoning}
          </p>
        </div>

        {/* Document Classifications */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          {classifications.map((doc, idx) => (
            <div
              key={idx}
              className="p-4 rounded-lg border"
              style={{
                backgroundColor: `${colors.midnight.light}40`,
                borderColor: `${colors.apollo.primary}30`,
              }}
            >
              <div className="flex items-start gap-3">
                <FileText size={20} style={{ color: colors.apollo.primary, marginTop: '2px' }} />
                <div className="flex-1 space-y-1">
                  <p style={{ ...typography.label, color: colors.text.primary }}>
                    {doc.document_name}
                  </p>
                  <p style={{ fontSize: '0.875rem', color: colors.text.secondary }}>
                    Domain: {doc.document_type} • {Array.isArray(doc.domain) ? doc.domain.join(', ') : doc.domain}
                  </p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {doc.key_topics.slice(0, 3).map((topic, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded text-xs"
                        style={{
                          backgroundColor: `${colors.apollo.accent}30`,
                          color: colors.apollo.primary,
                        }}
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Extraction Prompt */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="space-y-3"
        >
          <div className="relative flex items-center gap-2">
            <label style={{ ...typography.label, color: colors.text.primary }}>
              Extraction Prompt
            </label>
            <button
              onClick={() => setShowIntentionInfo(!showIntentionInfo)}
              className="transition-colors"
              style={{ color: colors.text.secondary }}
              aria-label="Show intention information"
            >
              <Info size={16} />
            </button>
            <AnimatePresence>
              {showIntentionInfo && (
                <InfoPopup title="What is an Extraction Prompt?">
                  <p>
                    This is the main prompt for the LLM. A good prompt clearly describes the document and the goal, which helps the AI generate a more accurate schema for you.
                    <br /><br />
                    <strong>Example:</strong> "Extract the line items, total amount, and vendor name from an invoice."
                  </p>
                </InfoPopup>
              )}
            </AnimatePresence>
          </div>

          <input
            type="text"
            value={intention}
            onChange={(e) => {
              setIntention(e.target.value);
              setIsEditing(true);
            }}
            className="w-full px-4 py-3 rounded-lg border outline-none transition-all"
            style={{
              backgroundColor: colors.midnight.deep,
              borderColor: `${colors.apollo.primary}40`,
              color: colors.text.primary,
              ...typography.body,
            }}
            placeholder="What data do you want to extract?"
          />
        </motion.div>

        {/* Schema Fields */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="relative flex items-center gap-2">
              <label style={{ ...typography.label, color: colors.text.primary }}>
                Extraction Schema ({fields.length} fields)
              </label>
              <button
                onClick={() => setShowSchemaInfo(!showSchemaInfo)}
                className="transition-colors"
                style={{ color: colors.text.secondary }}
                aria-label="Show schema information"
              >
                <Info size={16} />
              </button>
              <AnimatePresence>
                {showSchemaInfo && (
                  <InfoPopup title="Schema Fields Explained">
                    <ul>
                      <li><strong>Field Name:</strong> The key for the data point (e.g., `invoice_number`). Use snake_case.</li>
                      <li><strong>Data Type:</strong> The expected type of the extracted data (string, number, list, etc.).</li>
                      <li><strong>Description:</strong> A clear explanation of what this field represents to guide the AI.</li>
                      <li><strong>Example:</strong> A sample value to show the AI the desired format (e.g., `INV-2025-001`).</li>
                    </ul>
                  </InfoPopup>
                )}
              </AnimatePresence>
            </div>

            <button
              onClick={addField}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all hover:opacity-80"
              style={{
                backgroundColor: `${colors.apollo.primary}20`,
                color: colors.apollo.primary,
                ...typography.label,
              }}
            >
              <Plus size={16} />
              Add Field
            </button>
          </div>

          {/* Column Headers with Info Popups */}
          <div
            className="grid grid-cols-12 gap-3 px-4 pb-2"
            style={{
              color: colors.text.secondary,
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            {/* Field Name Header */}
            <div className="col-span-3 relative flex items-center gap-1">
              <span>Field Name</span>
              <button onClick={() => handleInfoToggle('fieldName')} aria-label="Info about Field Name">
                <Info size={12} />
              </button>
              <AnimatePresence>
                {activeInfoPopup === 'fieldName' && (
                  <InfoPopup title="Field Name">
                    <p>The key for the data point (e.g., `invoice_number`). It's best to use snake_case for consistency.</p>
                  </InfoPopup>
                )}
              </AnimatePresence>
            </div>

            {/* Data Type Header */}
            <div className="col-span-2 relative flex items-center gap-1">
              <span>Data Type</span>
              <button onClick={() => handleInfoToggle('dataType')} aria-label="Info about Data Type">
                <Info size={12} />
              </button>
              <AnimatePresence>
                {activeInfoPopup === 'dataType' && (
                  <InfoPopup title="Data Type">
                    <p>The expected type of the extracted data. This helps in validating the output. Common types are string, number, and list.</p>
                  </InfoPopup>
                )}
              </AnimatePresence>
            </div>

            {/* Description Header */}
            <div className="col-span-4 relative flex items-center gap-1">
              <span>Description</span>
              <button onClick={() => handleInfoToggle('description')} aria-label="Info about Description">
                <Info size={12} />
              </button>
              <AnimatePresence>
                {activeInfoPopup === 'description' && (
                  <InfoPopup title="Description">
                    <p>An explanation of what is expected to be extracted. This is crucial and helps AI to understand what you need. Need a shorter description for this field? Just mention "short" or specify below 20 words.</p>
                  </InfoPopup>
                )}
              </AnimatePresence>
            </div>

            {/* Example Header */}
            <div className="col-span-2 relative flex items-center gap-1">
              <span>Example</span>
              <button onClick={() => handleInfoToggle('example')} aria-label="Info about Example">
                <Info size={12} />
              </button>
              <AnimatePresence>
                {activeInfoPopup === 'example' && (
                  <InfoPopup title="Example Value">
                    <p>A sample value that shows the AI the desired format (e.g., `INV-2025-001` or `YYYY-MM-DD`).</p>
                  </InfoPopup>
                )}
              </AnimatePresence>
            </div>

            <div className="col-span-1"></div>
          </div>


          <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
            <AnimatePresence>
              {fields.map((field, idx) => (
                <motion.div
                  key={idx}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.2 }}
                  className="p-4 rounded-lg border"
                  style={{
                    backgroundColor: colors.midnight.light,
                    borderColor: `${colors.apollo.primary}30`,
                  }}
                >
                  <div className="grid grid-cols-12 gap-3 items-start">
                    <input
                      className="col-span-3 px-2 py-1 rounded bg-transparent border outline-none"
                      style={{ borderColor: `${colors.apollo.primary}20`, color: colors.text.primary }}
                      value={field.field_name}
                      onChange={(e) => updateField(idx, { field_name: e.target.value })}
                      placeholder="field_name"
                    />

                    <select
                      className="col-span-2 px-2 py-1 rounded bg-transparent border outline-none appearance-none"
                      style={{
                        borderColor: `${colors.apollo.primary}20`,
                        color: colors.text.primary,
                        backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23${colors.text.secondary.substring(1)}' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                        backgroundPosition: 'right 0.5rem center',
                        backgroundRepeat: 'no-repeat',
                        backgroundSize: '1.5em 1.5em',
                        paddingRight: '2rem'
                      }}
                      value={field.data_type}
                      onChange={(e) => updateField(idx, { data_type: e.target.value })}
                    >
                      <option style={{ backgroundColor: colors.midnight.deep }} value="string">string</option>
                      <option style={{ backgroundColor: colors.midnight.deep }} value="number">number</option>
                      <option style={{ backgroundColor: colors.midnight.deep }} value="boolean">boolean</option>
                      <option style={{ backgroundColor: colors.midnight.deep }} value="list">list</option>
                      <option style={{ backgroundColor: colors.midnight.deep }} value="object">object</option>
                    </select>

                    <input
                      className="col-span-4 px-2 py-1 rounded bg-transparent border outline-none"
                      style={{ borderColor: `${colors.apollo.primary}20`, color: colors.text.secondary }}
                      value={field.description}
                      onChange={(e) => updateField(idx, { description: e.target.value })}
                      placeholder="Description"
                    />

                    <input
                      className="col-span-2 px-2 py-1 rounded bg-transparent border outline-none"
                      style={{ borderColor: `${colors.apollo.primary}20`, color: colors.text.secondary }}
                      value={field.example}
                      onChange={(e) => updateField(idx, { example: e.target.value })}
                      placeholder="Example"
                    />

                    <button
                      onClick={() => removeField(idx)}
                      className="col-span-1 flex items-center justify-center p-1 rounded hover:bg-red-500/20 transition-colors"
                      style={{ color: colors.text.secondary }}
                    >
                      <X size={16} />
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="flex items-center gap-4 justify-center pt-4"
        >
          {isEditing && (
            <motion.div initial={{ opacity: 0, width: 0 }} animate={{ opacity: 1, width: 'auto' }} exit={{ opacity: 0, width: 0 }}>
              <button
                onClick={handleSaveChanges}
                className="px-6 py-3 rounded-lg transition-all hover:opacity-80 flex items-center gap-2"
                style={{
                  backgroundColor: `${colors.apollo.accent}40`,
                  color: colors.apollo.primary,
                  ...typography.button,
                }}
              >
                <Check size={20} />
                Save Changes
              </button>
            </motion.div>
          )}

          <button
            onClick={handleConfirm}
            className="px-8 py-3 rounded-lg transition-all hover:opacity-90 flex items-center gap-2"
            style={{
              backgroundColor: colors.apollo.primary,
              color: colors.midnight.deep,
              ...typography.button,
              boxShadow: `0 0 20px ${colors.apollo.primary}40`,
            }}
          >
            <Sparkles size={20} />
            Confirm & Extract
          </button>
        </motion.div>

        {/* Confidence Badge */}
        <div className="text-center">
          <span
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm"
            style={{
              backgroundColor: `${colors.apollo.accent}20`,
              color: colors.apollo.primary,
            }}
          >
            AI Confidence: {(recommendation.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </motion.div>
    </div>
  );
};