# UI Optimization & Manager Messaging System

## 1. Card Editor Layout Refactor
**Goal**: Optimize vertical space in the right column and balance the "Project Cycle" vs "Deliverables" height.

- **Refactor Right Column Grid**:
    - Change the layout of "Project Cycle" (项目周期) and "Departments" (参与部门) to be side-by-side (`grid-cols-2`).
    - This will reduce the vertical space consumed by short metadata fields.
    - Ensure "Deliverables" (输出物) fills the remaining vertical space (`flex-1`) with a minimum height to prevent it from being too cramped.
    - **Proposed Layout**:
      ```html
      <!-- Top Row: Cycle & Depts -->
      <div class="grid grid-cols-2 gap-4">
          <CardSection title="项目周期" ... />
          <CardSection title="参与部门" ... />
      </div>
      <!-- Middle: Products -->
      <CardSection title="相关产品及解决方案" ... />
      <!-- Bottom: Deliverables (fills rest) -->
      <div class="flex-1 min-h-0 relative">
          <CardSection title="输出物" ... class="h-full" />
      </div>
      ```

## 2. Card Editor Style Customization
**Goal**: Provide granular control over the visual appearance of the card.

- **Enhance `CardSection.vue`**:
    - Update props to accept a `config` object containing `fontSize`, `contentColor`, etc.
    - Apply `style="{ fontSize: config.fontSize + 'px' }"` to the content area.
- **Update `CardEditor.vue`**:
    - Add a **"Style Settings" (样式设置)** dropdown menu to the toolbar.
    - **Controls**:
        - **Font Size (字号)**: Slider or predefined sizes (Small/Medium/Large).
        - **Border Color (边框色)**: Color picker (updates `currentTheme.borderColor`).
        - **Background Color (背景色)**: Color picker (updates `currentTheme.backgroundColor`).
    - **State**: Bind these controls to the `currentTheme` or a new `styleConfig` object passed to all `CardSection` components.

## 3. Manager Messaging System (Personal Center)
**Goal**: Allow managers to publish messages and display them as rolling notifications.

- **Messaging Logic (Frontend Mock)**:
    - Use `localStorage` to store messages for demonstration purposes (simulating a backend).
    - Data Structure: `{ id, type: 'system'|'normal', target: 'all'|'dept', content, timestamp, isRead }`.
- **Publish UI ("Manager Mode")**:
    - Add a "发布消息" (Publish Message) button in the Personal Center (simulating Manager view).
    - **Modal Form**:
        - **Target**: Dropdown (All Company, Sales Dept, Specific User).
        - **Type**: Radio (System Notification, Normal Message).
        - **Content**: Textarea.
- **Notification Display**:
    - **Rolling Effect**: Implement a vertical marquee or fading list in the "System Notifications" box.
    - **Filtering**: Show only messages from **Today** OR **Unread** messages.
    - **Styling**: Distinguish "System" (Red/Bold) vs "Normal" (Blue/Regular) messages.

## 4. Execution Steps
1.  **Modify `CardSection.vue`** to support font size and extended styling.
2.  **Modify `CardEditor.vue`** to implement the new layout and add the Style Settings menu.
3.  **Modify `PersonalCenter.vue`** to add the Message Publisher and Rolling Notification display.
4.  **Verification**: Check layout balance, test style changes, and verify message publishing/display flow.
