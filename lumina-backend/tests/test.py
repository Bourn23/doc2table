"""
Step 1. Document Upload tests

curl -X POST -H "Content-Type: application/json" \
  -d '{"filenames": ["example1.pdf"]}' \
  http://localhost:8000/uploads/initiate
Expected Response:
    {"success":true,"session_id":1}

Step 1.1. Actual File Upload
curl -X POST -F "session_id=your-session-id" -F "file=@./example_documents/example1.pdf" http://localhost:8000/uploads/file
Expected Response:
    {"success":true,"filename":"example1.pdf","status":"UPLOADED"}

Step 1.2. Finalize Upload
curl -X POST http://localhost:8000/uploads/finalize/your-session-id
Expected Response:
    {"success":true,"message":"All files have been successfully uploaded and the session is ready."}

Step 2. Analyze Request (for suggestions/recommendations)
curl -X POST -H "Content-Type: application/json" -d '{"session_id": your-session-id}' http://localhost:8000/orchestrate/analyze
Expected Response:
    {"success":true,"message":"Document analysis and recommendation completed successfully.","classifications":[{"document_name":"example1.pdf","document_type":"research paper","domain":["animal behavior","cognition","zoology","public perception","animal welfare"],"key_topics":["zoo animal welfare","public attitudes","visitor experiences","behavioral intentions","mixed-methods systematic review","human factors","animal factors","environmental factors"],"data_types_present":["qualitative data","quantitative data","thematic synthesis","content analysis","peer reviewed journal articles"],"confidence":0.95}],"recommendation":{"recommended_intention":"Extract factors influencing zoo animal welfare and public perception, along with visitor experiences and behavioral intentions.","reasoning":"The documents are research papers primarily focused on zoo animal welfare, public attitudes, and visitor experiences. They utilize mixed-methods systematic reviews, indicating a need to capture both qualitative and quantitative data related to human, animal, and environmental factors influencing these aspects.","document_summary":"The documents collectively cover zoo animal welfare, public perception of animals in zoos, visitor experiences, and the behavioral intentions of visitors. They employ mixed-methods systematic reviews to analyze qualitative and quantitative data, focusing on human, animal, and environmental factors.","recommended_schema":[{"field_name":"factor_type","description":"Categorization of the factor influencing welfare or perception (e.g., Human, Animal, Environmental).","data_type":"string","unit":null,"example":"Environmental","validation_rules":"Enum: ['Human', 'Animal', 'Environmental', 'Other']"},{"field_name":"specific_factor","description":"The specific factor identified in the document (e.g., enclosure complexity, visitor noise, animal enrichment, keeper interaction).","data_type":"string","unit":null,"example":"Enclosure complexity","validation_rules":"None"},{"field_name":"influence_on","description":"The aspect of zoo animal welfare or public perception that the factor influences (e.g., animal welfare, visitor satisfaction, behavioral intentions).","data_type":"string","unit":null,"example":"Animal welfare","validation_rules":"None"},{"field_name":"direction_of_influence","description":"Whether the factor has a positive or negative influence.","data_type":"string","unit":null,"example":"Positive","validation_rules":"Enum: ['Positive', 'Negative', 'Neutral', 'Mixed']"}],"confidence":0.95}}

Step 3. (Optonal) Customize Extraction Schema
curl -X POST -H "Content-Type: application/json" \
-d '{
  "session_id": your-session-id,
  "intention": "Extract factors influencing zoo animal welfare and public perception. (User modified intention)",
  "fields": [
    {
      "field_name": "factor_type",
      "description": "Categorization of the factor influencing welfare or perception (e.g., Human, Animal, Environmental).",
      "data_type": "string",
      "unit": null,
      "example": "Environmental",
      "validation_rules": "Enum: [\"Human\", \"Animal\", \"Environmental\", \"Other\"]"
    },
    {
      "field_name": "specific_factor",
      "description": "The specific factor identified. **(USER EDITED THIS DESCRIPTION)**",
      "data_type": "string",
      "unit": null,
      "example": "Enclosure complexity",
      "validation_rules": "None"
    },
    {
      "field_name": "influence_on",
      "description": "The aspect of zoo animal welfare or public perception that the factor influences (e.g., animal welfare, visitor satisfaction, behavioral intentions).",
      "data_type": "string",
      "unit": null,
      "example": "Animal welfare",
      "validation_rules": "None"
    },
    {
      "field_name": "direction_of_influence",
      "description": "Whether the factor has a positive or negative influence.",
      "data_type": "string",
      "unit": null,
      "example": "Positive",
      "validation_rules": "Enum: [\"Positive\", \"Negative\", \"Neutral\", \"Mixed\"]"
    },
    {
      "field_name": "publication_year",
      "description": "The year the research paper was published. **(NEW FIELD ADDED BY USER)**",
      "data_type": "integer",
      "unit": null,
      "example": "2023",
      "validation_rules": "Must be a 4-digit year."
    }
  ]
}' \
http://localhost:8000/orchestrate/update_schema
Expected Response:
    {"success":true,"message":"Schema updated successfully."}

Step 4. Extraction Request
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "session_id": your-session-id,
    "intention": "Extract factors influencing public perception of zoo animal welfare and visitor behavioral intentions."
  }' \
  http://localhost:8000/orchestrate/extract
Expected Response:
    {"job_id":"e114dfb1-d46e-43de-999c-b4a08420168d","message":"Extraction job initiated."}

Step 5. Check Job Status via WebSocket
curl http://localhost:8000/jobs/your-new-job-id/status

Step 6. Indexing Extracted Data for RAG
curl -X POST -H "Content-Type: application/json" \  -d '{"session_id": your-session-id}' \
  http://localhost:8000/orchestrate/index
Expected Response:
    {"job_id":"fadac984-1ff3-4fc1-8a8a-c0a59a9d9598","message":"Indexing job initiated."}

(Optional): test job status
curl http://localhost:8000/jobs/616ebece-6487-4e69-bcfb-690080970830/status
Expected Response:
    {"job_id":"616ebece-6487-4e69-bcfb-690080970830","service":"indexing","status":"COMPLETED","message":"Successfully created 7 indexes.","timestamp":1761913039.1693788,"result":null}

Step 7. Querying the Data

Mode 1: RAG Query
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": 2, "query": "What are categories influencing public perception?", "num_results": 3}' \
  http://localhost:8000/orchestrate/query
  
Expected Response:
    {"success":true,"query":"What are categories influencing public perception?","answer":"The categories influencing public perception are:\n- Ethical considerations (beliefs about captivity and animal rights)\n- Direct human-animal interaction\n- Inappropriate visitor behavior\n- Disproportionate suffering (suitability of taxa for captivity)\n- Animal behavior (active and natural vs. abnormal or inactive)\n- Apparent health status\n- The facility (zoo purpose and advertisement, facility size)\n- The exhibit (naturalistic enclosure, enclosure size, enrichment, group size, condition of enclosure, diet, sensory stressors, temperature)\n- Welfare interpretation (educational material)","confidence":-6.24609375,"sources":[{"chunk_id":0,"score":-6.24609375,"text_preview":"All data for the column 'Specific Factor':\n\n- Record ID 0: Ethical considerations (beliefs about captivity and animal rights)\n- Record ID 1: Direct human-animal interaction\n- Record ID 2: Inappropriat..."}],"relevant_records":[{"chunk_id":0,"text":"All data for the column 'Specific Factor':\n\n- Record ID 0: Ethical considerations (beliefs about captivity and animal rights)\n- Record ID 1: Direct human-animal interaction\n- Record ID 2: Inappropriate visitor behavior\n- Record ID 3: Disproportionate suffering (suitability of taxa for captivity)\n- Record ID 4: Animal behavior (active and natural vs. abnormal or inactive)\n- Record ID 5: Apparent health status\n- Record ID 6: The facility (zoo purpose and advertisement, facility size)\n- Record ID 7: The exhibit (naturalistic enclosure, enclosure size, enrichment, group size, condition of enclosure, diet, sensory stressors, temperature)\n- Record ID 8: Welfare interpretation (educational material)\n- Record ID 9: Impact of welfare perceptions on visitor experience and behavior","score":-6.24609375}],"result_type":"rag","function_result":null}
    
Mode 2: Function Execution Query (to export data for now)
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": 2, "query": "can you export this as csv?", "num_results": 3}' \
  http://localhost:8000/orchestrate/query
  
Expected Response:
    {"success":true,"query":"can you export this as csv?","answer":"Successfully exported 10 records to session_2_export_20251031_124344.csv","confidence":1.0,"sources":null,"relevant_records":null,"result_type":"function","function_result":{"success":true,"message":"Successfully exported 10 records to session_2_export_20251031_124344.csv","filepath":"exports/session_2_export_20251031_124344.csv","record_count":10,"field_name":null,"records_updated":null,"sample_values":null,"new_field":null,"new_records":null,"new_job_id":null}}

Mode 3: RAG over non-existing results
curl -X POST -H "Content-Type: application/json" \
  -d '{"session_id": your-session-id, "query": "What specific places were studied?", "num_results": 3}' \
  http://localhost:8000/orchestrate/query
Expected Response:
    {"success":true,"query":"What specific places were studied?","answer":"I've started a new job to find and add the field 'specific_places'. You can track its progress.","confidence":1.0,"sources":[],"relevant_records":[],"result_type":"function_job_start","function_result":{"success":true,"message":"Dynamic column extraction job has been started.","filepath":null,"record_count":null,"field_name":null,"records_updated":null,"sample_values":null,"new_field":null,"new_records":null,"new_job_id":"1ee96502-a675-4446-8009-aaee5260a341"}}
Then, check job status to get results:
    curl http://localhost:8000/jobs/1ee96502-a675-4446-8009-aaee5260a341/status



"""