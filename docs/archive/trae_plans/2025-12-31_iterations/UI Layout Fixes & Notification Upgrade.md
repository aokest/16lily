# UI Layout Fixes & Notification System Upgrade

## 1. Card Editor "Deliverables" Layout Fix
**Goal**: Address the user's requirement to reposition the "Deliverables" (输出物) section to span across columns or utilize space better, and remove "CONFIDENTIAL".

- **Layout Strategy**:
    - The user provided a sketch implying "Deliverables" should be at the bottom, potentially full width or better utilized.
    - **Current Layout**: 
      - Left Col (7): Goal, Analysis, Content, Support, Budget.
      - Right Col (5): Cycle, Depts, Products, Deliverables.
    - **Proposed Layout (Refined)**:
      - Keep the 2-column grid for the upper section.
      - Move "Deliverables" (输出物) **out of the right column** and place it at the **bottom of the entire grid**, spanning full width (`col-span-12`).
      - This allows "Deliverables" to grow vertically or flow horizontally as needed without being cramped in the narrow right column.
      - **Grid Structure Change**:
        ```html
        <div class="grid grid-cols-12 gap-4">
           <!-- Top Left (7) -->
           <!-- Top Right (5) -->
           <!-- Bottom Full Width (12) -->
           <div class="col-span-12 mt-4">
              <CardSection title="输出物" ... />
           </div>
        </div>
        ```
- **Footer Cleanup**:
    - Remove the "CONFIDENTIAL" text and "PROJECT CARD" watermark entirely as requested.
- **Style Button Visibility**:
    - The user insists the style button is missing. I will verify if `lucide-vue-next` or similar icon library is correctly rendering `settings-2`.
    - I will force a re-render or check if the container width is hiding it.
    - I will ensure the button is explicitly visible without conditional logic errors.

## 2. Notification System Upgrade (Title + Body)
**Goal**: Upgrade the messaging system to support structured messages (Title + Body) and click-to-view functionality.

- **Data Structure Update**:
    - Update `publishForm` to include `title` and `content`.
    - Update `messages` array structure: `{ id, title, content, type, ... }`.
- **UI Update - Publish Modal**:
    - Add an input field for **"消息标题" (Title)**.
    - Rename existing textarea to **"消息正文" (Body)**.
- **UI Update - Notification List**:
    - Display **Title** in the list view (bold).
    - Display a truncated **Body** or "Click to view" hint.
    - Add `cursor-pointer` to list items.
- **Interaction - View Detail**:
    - Add a **"View Message" Dialog**:
        - clicking a notification opens this dialog showing full Title, Body, Sender/Target info, and Time.

## 3. Execution Steps
1.  **Modify `CardEditor.vue`**:
    - Implement the full-width bottom layout for "Deliverables".
    - Delete footer watermarks.
    - Verify Style button (maybe move it out of the `relative` group if z-index is an issue, or just ensure it's rendered).
2.  **Modify `PersonalCenter.vue`**:
    - Update `publishForm` and `messages` state.
    - Add "Title" input to Publish Dialog.
    - Create a new "Message Detail" Dialog.
    - Update list rendering to show Title and handle clicks.
3.  **Verification**:
    - Check "Deliverables" layout space.
    - Verify Message flow (Publish -> List -> Click -> Detail).
