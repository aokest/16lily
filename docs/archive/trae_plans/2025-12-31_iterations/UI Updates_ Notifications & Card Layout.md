# UI Updates Plan

## 1. Notification Center (PersonalCenter.vue)
**Goal**: Add a "Mark All Read" or "View All" interaction, and visually distinguish "Unread" vs "Read" messages, plus add an explicit "All Messages" button/link.

- **Current State**: 
    - Has "全部已读" (Mark All Read) button.
    - Has "发布" (Publish) button.
    - List filters by `filteredMessages` (Today OR Unread).
- **Changes**:
    - **Header**:
        - Keep "发布" (Publish).
        - **Add** a button: "全部消息" (All Messages) -> toggles view or opens a full list modal. 
        - Keep "全部已读" (Mark All Read).
    - **List View**:
        - **Unread**: Show with a blue dot or bold text.
        - **Read**: Grayed out or normal text.
        - **Logic**: Modify `filteredMessages` logic or provide a toggle to show "All" vs "Unread Only". The user asked for "All Messages" button, likely meaning a way to see history.
        - **Implementation**: 
            - Add `showAllMessages` boolean state. 
            - If `showAllMessages` is true, show all. Else show Today/Unread.
            - "全部消息" button toggles this state.
    - **Language**: Ensure all UI text is Chinese.

## 2. Card Editor Layout (CardEditor.vue)
**Goal**: Strictly follow the user's red-box diagram for "Deliverables" (输出物) placement.

- **User Directive**: "Strictly follow the red box... size... do not put it at the very bottom."
- **Analysis of User's Image (Fig 2)**:
    - The red box for "输出物" (Deliverables) is in the **Bottom Right** quadrant of the grid, taking up substantial space, but **NOT** spanning the full width of the card.
    - It seems to replace the "Related Products" or sit below it, but aligned to the **Right Column**.
    - **Wait**, looking closely at the previous code:
        - I moved it to `col-span-12` (full width bottom). The user says "Do NOT put it at the very bottom".
        - This implies they want it back in the **Right Column**, but with **more vertical space**.
    - **Re-evaluating the red box**:
        - The red box in the user's image is in the **bottom right corner**.
        - It is **tall**.
        - It says "If space is not enough... arrange in another column".
    - **Correct Layout Interpretation**:
        - **Left Column**: Goal, Analysis, Content, Support, Budget.
        - **Right Column**: Cycle, Depts, Products... **AND Deliverables**.
        - **Deliverables** should be the last item in the **Right Column**, but it needs to **grow** to fill the remaining height of the card, matching the height of the left column's content.
        - The `min-h-0` on the right column container + `flex-1` on the Deliverables wrapper is the correct Flexbox approach to make it fill the remaining vertical space.
- **Action**:
    - Revert the `col-span-12` change.
    - Put "Deliverables" back into the **Right Column**.
    - Ensure the Right Column uses `flex flex-col h-full`.
    - Set "Deliverables" container to `flex-1` so it expands to fill the bottom-right corner, ensuring the card bottom aligns with the left column.

## 3. Execution Steps
1.  **Modify `PersonalCenter.vue`**:
    - Add "全部消息" button.
    - Implement toggle logic for message filtering.
    - Ensure Read/Unread visual distinction.
2.  **Modify `CardEditor.vue`**:
    - Move `CardSection title="输出物"` back to the **Right Column**.
    - Apply `flex-1` and `h-full` classes to ensure it occupies all remaining vertical space in that column.
    - Verify spacing matches the user's "red box" intent (bottom right, tall).
3.  **Verification**:
    - Check Message filter toggle.
    - Check Card Editor layout (Deliverables in bottom right, filling space).
