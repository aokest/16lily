I have reviewed the documentation as requested.

### Analysis
1.  **`docs/TODO_LIST.md`**:
    *   **Verdict**: **Redundant and Outdated**.
    *   **Reasoning**: Most items (Competition/Market Activity models, AI entry) are already completed. The remaining valid items (Data Migration) are already covered in the "Next Steps" section of `PROJECT_TRACKING.md`.
    *   **Action**: Delete this file to avoid confusion.

2.  **`docs/TECHNICAL_DOCS.md`**:
    *   **Verdict**: **Needs Update**.
    *   **Reasoning**:
        *   **AI Integration (Section 3.5)** describes an old "Signal-based" approach (using `pre_save` and `ai_raw_text` field). The current system uses a modern "API-based" approach (Frontend Chat Interface -> API -> AI Service).
        *   **Prompt Management**: Lacks description of the new `PromptTemplate` model and decoupling logic.
    *   **Action**: Rewrite Section 3.5 and add details about Prompt Templates.

### Plan
1.  **Delete** `docs/TODO_LIST.md`.
2.  **Update** `docs/TECHNICAL_DOCS.md` to reflect the latest AI architecture (Chat-to-Form API, PromptTemplates) and remove obsolete Signal-based logic.