"""AI Service - Claude AI integration for natural language understanding.

This module provides Claude AI integration for the project manager CLI,
enabling natural language understanding and intelligent roadmap management.

Example:
    >>> from coffee_maker.cli.ai_service import AIService
    >>>
    >>> service = AIService()
    >>> response = service.process_request(
    ...     user_input="Add a priority for user authentication",
    ...     context={'roadmap_summary': summary},
    ...     history=[]
    ... )
    >>> print(response.message)
"""

import logging
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from anthropic import Anthropic

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """AI response with optional action.

    Attributes:
        message: Response message from Claude
        action: Optional structured action to execute
        confidence: Confidence score (0.0-1.0)
    """

    message: str
    action: Optional[Dict] = None
    confidence: float = 1.0


class AIService:
    """Claude AI service for natural language understanding.

    This service provides intelligent roadmap management through natural
    language processing using Claude AI.

    Attributes:
        model: Claude model to use
        max_tokens: Maximum tokens per response
        client: Anthropic API client

    Example:
        >>> service = AIService()
        >>> response = service.process_request(
        ...     "What should we work on next?",
        ...     context={'roadmap_summary': {...}},
        ...     history=[]
        ... )
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4000,
    ):
        """Initialize AI service.

        Args:
            model: Claude model to use
            max_tokens: Maximum tokens per response
        """
        self.model = model
        self.max_tokens = max_tokens

        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. " "Please set it in your .env file or environment."
            )

        self.client = Anthropic(api_key=api_key)

        logger.info(f"AIService initialized with model: {model}")

    def process_request(self, user_input: str, context: Dict, history: List[Dict]) -> AIResponse:
        """Process user request with AI.

        Args:
            user_input: User's natural language input
            context: Current roadmap context (summary, priorities, etc.)
            history: Conversation history

        Returns:
            AIResponse with message and optional action

        Example:
            >>> response = service.process_request(
            ...     "Add a priority for authentication",
            ...     context={'roadmap_summary': summary},
            ...     history=[]
            ... )
            >>> if response.action:
            ...     print(f"Action: {response.action['type']}")
        """
        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Build conversation messages
            messages = self._build_messages(user_input, history)

            logger.debug(f"Processing request: {user_input[:100]}...")

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            )

            # Extract content
            content = response.content[0].text

            logger.info(f"AI response generated ({len(content)} chars)")

            # Extract action if present
            action = self._extract_action(content)

            return AIResponse(message=content, action=action)

        except Exception as e:
            logger.error(f"AI request failed: {e}")
            return AIResponse(
                message=f"Sorry, I encountered an error: {str(e)}",
                action=None,
                confidence=0.0,
            )

    def classify_intent(self, user_input: str) -> str:
        """Classify user intent based on input.

        Uses simple keyword matching for intent classification.
        Could be enhanced with a small classification model.

        Args:
            user_input: User input text

        Returns:
            Intent category (add_priority, update_priority, view_roadmap, etc.)

        Example:
            >>> intent = service.classify_intent("Add a new priority")
            >>> print(intent)
            'add_priority'
        """
        lower_input = user_input.lower()

        # Intent patterns
        intents = {
            "add_priority": [
                "add",
                "create",
                "new priority",
                "insert priority",
            ],
            "update_priority": [
                "update",
                "change",
                "modify",
                "edit priority",
                "mark as",
            ],
            "view_roadmap": [
                "show",
                "view",
                "display",
                "see",
                "list",
                "what are",
            ],
            "analyze_roadmap": [
                "analyze",
                "health",
                "check",
                "status",
                "how is",
            ],
            "suggest_next": [
                "suggest",
                "recommend",
                "what next",
                "what should",
                "priority",
            ],
            "start_implementation": [
                "implement",
                "start",
                "begin",
                "work on",
                "build",
            ],
            "daemon_status": [
                "daemon",
                "running",
                "status",
                "progress",
            ],
        }

        # Check each intent pattern
        for intent, patterns in intents.items():
            if any(pattern in lower_input for pattern in patterns):
                logger.debug(f"Classified intent: {intent}")
                return intent

        # Default to general query
        logger.debug("Classified intent: general_query")
        return "general_query"

    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with roadmap context.

        Args:
            context: Context dictionary with roadmap information

        Returns:
            System prompt string
        """
        roadmap_summary = context.get("roadmap_summary", {})

        total = roadmap_summary.get("total", 0)
        completed = roadmap_summary.get("completed", 0)
        in_progress = roadmap_summary.get("in_progress", 0)
        planned = roadmap_summary.get("planned", 0)

        prompt = f"""You are an AI project manager assistant for the Coffee Maker project.

Current Roadmap State:
- Total priorities: {total}
- Completed: {completed}
- In Progress: {in_progress}
- Planned: {planned}

Your Role:
1. Help users manage the roadmap through natural language
2. Provide strategic project management insights
3. Suggest priority additions, updates, or changes
4. Analyze roadmap health and identify issues
5. Give recommendations for next steps

Communication Style:
- Be strategic and proactive
- Always provide context and reasoning
- Identify dependencies and risks
- Give concrete, actionable recommendations
- Use clear, professional language

When users ask to modify the roadmap:
1. Analyze the request carefully
2. Consider impact and dependencies
3. Suggest specific actions with reasoning
4. Format responses clearly

Response Format:
- Use markdown for formatting
- Use bullet points for lists
- Use **bold** for emphasis
- Provide clear section headings

Always explain your reasoning before suggesting changes.
Be strategic - analyze impact, dependencies, and risks.
"""

        # Add priority list if available
        priorities = roadmap_summary.get("priorities", [])
        if priorities:
            prompt += "\n\nCurrent Priorities:\n"
            for p in priorities[:10]:  # Limit to first 10
                prompt += f"- {p['number']}: {p['title']} ({p['status']})\n"

        return prompt

    def _build_messages(self, user_input: str, history: List[Dict]) -> List[Dict]:
        """Build conversation messages.

        Args:
            user_input: Current user input
            history: Conversation history

        Returns:
            List of message dictionaries for Claude API
        """
        messages = []

        # Add history (last 10 messages for context window)
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current input
        messages.append({"role": "user", "content": user_input})

        return messages

    def _extract_action(self, content: str) -> Optional[Dict]:
        """Extract structured action from AI response.

        Looks for XML-like action tags in the response:
        <action type="add_priority" priority="PRIORITY X" .../>

        Args:
            content: AI response content

        Returns:
            Action dictionary or None

        Example:
            >>> action = self._extract_action(
            ...     "Let's add it. <action type='add_priority' priority='10'/>"
            ... )
            >>> print(action['type'])
            'add_priority'
        """
        if "<action" not in content:
            return None

        try:
            # Parse action attributes
            match = re.search(r"<action\s+(.+?)/>", content, re.DOTALL)
            if not match:
                return None

            attrs_str = match.group(1)

            # Parse attributes: type="..." priority="..." etc.
            attrs = {}
            for attr_match in re.finditer(r'(\w+)=["\']([^"\']+)["\']', attrs_str):
                attrs[attr_match.group(1)] = attr_match.group(2)

            logger.debug(f"Extracted action: {attrs}")
            return attrs

        except Exception as e:
            logger.warning(f"Failed to extract action: {e}")
            return None

    def check_available(self) -> bool:
        """Check if AI service is available.

        Returns:
            True if API key is configured and accessible

        Example:
            >>> if service.check_available():
            ...     print("AI service ready!")
        """
        try:
            # Try a minimal API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
            )

            logger.info(f"AI service available: {response.model}")
            return True

        except Exception as e:
            logger.error(f"AI service not available: {e}")
            return False
