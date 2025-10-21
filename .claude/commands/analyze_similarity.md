You are analyzing similarity between a draft user story and existing user stories.

DRAFT USER STORY:
Title: $DRAFT_TITLE
Description: $DRAFT_DESCRIPTION

EXISTING USER STORIES:
$EXISTING_STORIES

TASK:
Analyze semantic similarity between the draft and each existing user story.
Consider:
- Similar functionality or features
- Overlapping user needs
- Duplicate or redundant work
- Related but distinct features

FORMAT YOUR RESPONSE AS:

[US-ID]: [0-100%] - [Brief reason for similarity score]

Example:
US-042: 85% - Both involve PDF export functionality
US-015: 45% - Related to reporting but different feature
US-008: 10% - Unrelated

Only include user stories with >40% similarity.
