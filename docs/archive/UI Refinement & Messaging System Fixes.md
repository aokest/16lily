# UI Refinement & Manager Messaging System Fixes

## 1. Card Editor Layout & Style Fixes
**Goal**: Resolve layout overlaps, adjust "Deliverables" box spacing, and ensure style controls are accessible.

- **Footer Spacing & Overlap**:
    - Modify `CardEditor.vue`:
    - Add a `pb-8` or `pb-10` to the right column container or the "Deliverables" wrapper to create hard separation from the footer.
    - Ensure the footer has a fixed height reservation or margin so content doesn't flow behind it.
- **Header Refactor**:
    - Change the header layout to put **Project Code** and **Project Number** on the same line to save vertical space and avoid overlapping the title.
    - Layout: `Flex Row (End aligned)` for metadata.
- **Style Settings Visibility**:
    - Verify the `showStyleMenu` button implementation. It appears correct in code, but I will double-check its placement in the template (ensure it's not hidden by `v-if` logic).
    - I will check the icon color (`text-gray-600`) to ensure it's visible against the background.

## 2. Manager Messaging System Enhancements
**Goal**: Fix the "Publish" modal to support selecting specific Users and Departments.

- **API Integration**:
    - Use `/api/admin/users/` (found in search) to fetch the user list.
    - Use `/api/departments/` (standard ViewSet assumption) or `/api/admin/departments/` to fetch the department list.
- **Modal Logic Update**:
    - **Target Selection**:
        - When `target === 'user_specific'`, show an `<el-select multiple filterable>` populated with users.
        - When `target === 'dept_specific'`, show an `<el-select multiple>` populated with departments.
    - **Publish Button**:
        - Increase prominence: Change to `type="primary"` (remove `plain`), maybe add `size="default"` or custom styling.
- **Data Handling**:
    - Mock the API calls if endpoints are restricted, but try to use real data first.
    - Store the selected `target_ids` in the message object (mock logic for now).

## 3. Execution Steps
1.  **Refactor `CardEditor.vue`**: Fix header layout, adjust bottom padding for "Output" section.
2.  **Update `PersonalCenter.vue`**:
    - Add `fetchUsers` and `fetchDepartments` functions.
    - Update the "Publish" modal form to include dynamic selectors.
    - Enhance the "Publish" button style.
3.  **Verify**: Check layout spacing and modal functionality.
