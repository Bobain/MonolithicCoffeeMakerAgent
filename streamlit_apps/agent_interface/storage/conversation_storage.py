"""Conversation storage for persisting chat history.

This module provides functionality to save and load conversations:
- Save conversations to JSON files
- Load previous conversations
- List all saved conversations
- Delete old conversations

Conversations are stored in the data/conversations/ directory.
"""

import json  # Keep for json.dumps in export_conversation
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from coffee_maker.utils.file_io import read_json_file, write_json_file


class ConversationStorage:
    """Handles persistence of conversation history.

    Conversations are stored as JSON files in the data/conversations/ directory.
    Each conversation has a unique ID and includes:
    - Conversation ID and timestamp
    - Agent configuration
    - Message history
    - Metrics (tokens, cost)

    Attributes:
        storage_dir: Directory where conversations are stored
    """

    def __init__(self, storage_dir: Optional[Union[str, Path]] = None):
        """Initialize conversation storage.

        Args:
            storage_dir: Directory for storing conversations.
                        Defaults to data/conversations/
        """
        if storage_dir is None:
            # Default to data/conversations relative to project root
            project_root = Path(__file__).parents[3]
            storage_dir_path = project_root / "data" / "conversations"
        else:
            storage_dir_path = Path(storage_dir)

        self.storage_dir = storage_dir_path
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_conversation(
        self, conversation_id: str, agent_name: str, config: Dict, messages: List[Dict], metrics: Dict
    ) -> str:
        """Save a conversation to disk.

        Args:
            conversation_id: Unique conversation identifier
            agent_name: Name of the agent
            config: Agent configuration
            messages: List of message dictionaries
            metrics: Conversation metrics

        Returns:
            Path to saved conversation file

        Example:
            >>> storage = ConversationStorage()
            >>> path = storage.save_conversation(
            ...     "conv-123",
            ...     "Code Reviewer",
            ...     {"model": "claude-sonnet-4"},
            ...     [{"role": "user", "content": "Hello"}],
            ...     {"tokens": 100, "cost": 0.01}
            ... )
        """
        conversation_data = {
            "id": conversation_id,
            "agent_name": agent_name,
            "config": config,
            "messages": messages,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
        }

        # Create filename with timestamp and ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{conversation_id[:8]}.json"
        filepath = self.storage_dir / filename

        # Save to JSON
        write_json_file(filepath, conversation_data)

        return str(filepath)

    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load a conversation by ID.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Conversation data dictionary, or None if not found

        Example:
            >>> storage = ConversationStorage()
            >>> conv = storage.load_conversation("conv-123")
            >>> if conv:
            ...     print(conv["messages"])
        """
        # Find file matching conversation ID
        for filepath in self.storage_dir.glob("*.json"):
            data = read_json_file(filepath, default=None)
            if data and data.get("id") == conversation_id:
                return data

        return None

    def load_conversation_by_file(self, filename: str) -> Optional[Dict]:
        """Load a conversation from a specific file.

        Args:
            filename: Name of the conversation file

        Returns:
            Conversation data dictionary, or None if file doesn't exist
        """
        filepath = self.storage_dir / filename

        if not filepath.exists():
            return None

        return read_json_file(filepath, default=None)

    def list_conversations(self, limit: int = 50) -> List[Dict]:
        """List all saved conversations.

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation summaries, sorted by timestamp (newest first)

        Example:
            >>> storage = ConversationStorage()
            >>> conversations = storage.list_conversations(limit=10)
            >>> for conv in conversations:
            ...     print(f"{conv['timestamp']}: {conv['agent_name']}")
        """
        conversations = []

        for filepath in self.storage_dir.glob("*.json"):
            try:
                data = read_json_file(filepath, default=None)
                if not data:
                    continue

                # Create summary
                summary = {
                    "id": data.get("id"),
                    "filename": filepath.name,
                    "agent_name": data.get("agent_name"),
                    "timestamp": data.get("timestamp"),
                    "message_count": len(data.get("messages", [])),
                    "metrics": data.get("metrics", {}),
                }

                conversations.append(summary)

            except KeyError:
                # Skip invalid files
                continue

        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return conversations[:limit]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation by ID.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            True if deleted, False if not found

        Example:
            >>> storage = ConversationStorage()
            >>> deleted = storage.delete_conversation("conv-123")
            >>> if deleted:
            ...     print("Conversation deleted")
        """
        # Find and delete file matching conversation ID
        for filepath in self.storage_dir.glob("*.json"):
            try:
                data = read_json_file(filepath, default=None)
                if data and data.get("id") == conversation_id:
                    filepath.unlink()
                    return True
            except KeyError:
                continue

        return False

    def delete_old_conversations(self, days: int = 30) -> int:
        """Delete conversations older than specified days.

        Args:
            days: Delete conversations older than this many days

        Returns:
            Number of conversations deleted

        Example:
            >>> storage = ConversationStorage()
            >>> count = storage.delete_old_conversations(days=30)
            >>> print(f"Deleted {count} old conversations")
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for filepath in self.storage_dir.glob("*.json"):
            try:
                data = read_json_file(filepath, default=None)
                if not data:
                    continue

                timestamp_str = data.get("timestamp")

                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)

                    if timestamp < cutoff:
                        filepath.unlink()
                        deleted_count += 1

            except (KeyError, ValueError):
                continue

        return deleted_count

    def export_conversation(self, conversation_id: str, format: str = "markdown") -> Optional[str]:
        """Export a conversation to specified format.

        Args:
            conversation_id: Unique conversation identifier
            format: Export format ("markdown", "text", "json")

        Returns:
            Formatted conversation string, or None if not found
        """
        data = self.load_conversation(conversation_id)

        if not data:
            return None

        if format == "json":
            return json.dumps(data, indent=2)
        elif format == "markdown":
            return self._format_as_markdown(data)
        elif format == "text":
            return self._format_as_text(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _format_as_markdown(self, data: Dict) -> str:
        """Format conversation as Markdown."""
        lines = [
            f"# Conversation with {data['agent_name']}",
            "",
            f"**ID:** {data['id']}",
            f"**Date:** {data['timestamp']}",
            f"**Model:** {data['config'].get('model', 'unknown')}",
            "",
            "## Metrics",
            "",
            f"- Messages: {len(data['messages'])}",
            f"- Tokens: {data['metrics'].get('total_tokens', 0)}",
            f"- Cost: ${data['metrics'].get('total_cost', 0):.4f}",
            "",
            "---",
            "",
            "## Conversation",
            "",
        ]

        for msg in data["messages"]:
            role = msg["role"].title()
            content = msg["content"]
            lines.append(f"### {role}")
            lines.append("")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)

    def _format_as_text(self, data: Dict) -> str:
        """Format conversation as plain text."""
        lines = [
            f"Conversation with {data['agent_name']}",
            "=" * 70,
            f"ID: {data['id']}",
            f"Date: {data['timestamp']}",
            f"Model: {data['config'].get('model', 'unknown')}",
            f"Messages: {len(data['messages'])}",
            f"Tokens: {data['metrics'].get('total_tokens', 0)}",
            f"Cost: ${data['metrics'].get('total_cost', 0):.4f}",
            "",
            "=" * 70,
            "",
        ]

        for i, msg in enumerate(data["messages"], 1):
            role = msg["role"].upper()
            content = msg["content"]
            lines.append(f"[{i}] {role}:")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)

    def get_storage_stats(self) -> Dict:
        """Get statistics about stored conversations.

        Returns:
            Dictionary with storage statistics

        Example:
            >>> storage = ConversationStorage()
            >>> stats = storage.get_storage_stats()
            >>> print(f"Total conversations: {stats['count']}")
            >>> print(f"Total size: {stats['total_size_mb']:.2f} MB")
        """
        conversations = list(self.storage_dir.glob("*.json"))

        total_size = sum(f.stat().st_size for f in conversations)

        return {
            "count": len(conversations),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "storage_dir": str(self.storage_dir),
        }
