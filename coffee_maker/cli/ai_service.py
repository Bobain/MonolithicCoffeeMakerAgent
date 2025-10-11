"""AI Service - Claude AI integration for natural language understanding.

This module provides Claude AI integration for the project manager CLI,
enabling natural language understanding and intelligent roadmap management.

IMPORTANT: Communication Guidelines
    See docs/COLLABORATION_METHODOLOGY.md Section 4.6:
    - Use plain language, NOT technical shorthand (no "US-012")
    - Say "the email notification feature" not "US-012"
    - Always explain features descriptively to users

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
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from anthropic import Anthropic

from coffee_maker.config import ConfigManager

logger = logging.getLogger(__name__)

# Import Claude CLI interface (optional)
try:
    from coffee_maker.autonomous.claude_cli_interface import (
        ClaudeCLIInterface,
    )

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    logger.warning("ClaudeCLIInterface not available, API mode only")


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
        use_claude_cli: bool = False,
        claude_cli_path: str = "/opt/homebrew/bin/claude",
    ):
        """Initialize AI service.

        Args:
            model: Claude model to use
            max_tokens: Maximum tokens per response
            use_claude_cli: If True, use Claude CLI instead of API (default: False)
            claude_cli_path: Path to claude CLI executable (default: /opt/homebrew/bin/claude)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.use_claude_cli = use_claude_cli
        self.client = None
        self.cli_interface = None

        if use_claude_cli:
            # Use Claude CLI (subscription-based, no API credits needed)
            if not CLI_AVAILABLE:
                raise ValueError(
                    "Claude CLI mode requested but ClaudeCLIInterface not available. "
                    "Please check the import or use API mode instead."
                )

            # For CLI mode, convert model name to CLI alias if needed
            cli_model = model
            if "sonnet" in model.lower():
                cli_model = "sonnet"
            elif "opus" in model.lower():
                cli_model = "opus"
            elif "haiku" in model.lower():
                cli_model = "haiku"

            self.cli_interface = ClaudeCLIInterface(
                claude_path=claude_cli_path,
                model=cli_model,
                max_tokens=max_tokens,
            )

            logger.info(f"AIService initialized with Claude CLI: {cli_model}")

        else:
            # Use Anthropic API (requires API credits)
            try:
                api_key = ConfigManager.get_anthropic_api_key()
            except Exception as e:
                raise ValueError(
                    f"ANTHROPIC_API_KEY environment variable not set. "
                    f"Please set it in your .env file or environment. Error: {e}"
                ) from e

            self.client = Anthropic(api_key=api_key)

            logger.info(f"AIService initialized with Anthropic API: {model}")

    def process_request(self, user_input: str, context: Dict, history: List[Dict], stream: bool = True) -> AIResponse:
        """Process user request with AI.

        Args:
            user_input: User's natural language input
            context: Current roadmap context (summary, priorities, etc.)
            history: Conversation history
            stream: If True, returns a streaming response (default: True)

        Returns:
            AIResponse with message and optional action

        Example:
            >>> # Non-streaming (blocking)
            >>> response = service.process_request(
            ...     "Add a priority for authentication",
            ...     context={'roadmap_summary': summary},
            ...     history=[],
            ...     stream=False
            ... )
            >>> print(response.message)

            >>> # Streaming (progressive)
            >>> response = service.process_request(
            ...     "Explain the roadmap",
            ...     context=context,
            ...     history=[],
            ...     stream=True
            ... )
            >>> for chunk in response.stream_iterator:
            ...     print(chunk, end="")
        """
        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Build conversation messages
            messages = self._build_messages(user_input, history)

            logger.debug(f"Processing request: {user_input[:100]}...")

            if self.use_claude_cli:
                # Use Claude CLI interface
                # Build full prompt: system + history + user input
                full_prompt = system_prompt + "\n\n"

                # Add conversation history
                for msg in messages[:-1]:  # All except last (current user input)
                    role = msg["role"]
                    content = msg["content"]
                    full_prompt += f"\n{role.upper()}: {content}\n"

                # Add current user input
                full_prompt += f"\nUSER: {user_input}\n\nASSISTANT:"

                # Execute via CLI
                result = self.cli_interface.execute_prompt(full_prompt)

                if not result.success:
                    raise Exception(result.error)

                content = result.content

            else:
                # Use Anthropic API
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

    def process_request_stream(self, user_input: str, context: Dict, history: List[Dict]):
        """Process user request with AI streaming.

        Args:
            user_input: User's natural language input
            context: Current roadmap context
            history: Conversation history

        Yields:
            Text chunks as they arrive from Claude API

        Example:
            >>> for chunk in service.process_request_stream("Hello", context, []):
            ...     print(chunk, end="")
            Hello! How can I help you today?
        """
        try:
            if self.use_claude_cli:
                # Claude CLI doesn't support streaming, so we get the full response
                # and yield it in chunks to simulate streaming
                response = self.process_request(user_input, context, history, stream=False)

                # Yield in chunks of ~50 chars for better UX
                chunk_size = 50
                for i in range(0, len(response.message), chunk_size):
                    yield response.message[i : i + chunk_size]

                logger.info("CLI response yielded in chunks")
                return

            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Build conversation messages
            messages = self._build_messages(user_input, history)

            logger.debug(f"Processing streaming request: {user_input[:100]}...")

            # Stream from Claude API
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    yield text

            logger.info("Streaming response completed")

        except Exception as e:
            logger.error(f"Streaming request failed: {e}")
            yield f"\n\n❌ Sorry, I encountered an error: {str(e)}"

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
            "user_story": [
                "as a",
                "i want",
                "i need",
                "user story",
                "feature request",
                "so that",
            ],
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

    def extract_user_story(self, user_input: str) -> Optional[Dict]:
        """Extract User Story components from natural language.

        Uses Claude AI to parse natural language into structured User Story format.

        Args:
            user_input: Natural language description

        Returns:
            Dictionary with User Story components:
            {
                'role': 'developer',
                'want': 'deploy on GCP',
                'so_that': 'runs 24/7',
                'title': 'Deploy code_developer on GCP'
            }
            or None if can't extract

        Example:
            >>> story = service.extract_user_story(
            ...     "I want to deploy on GCP so it runs 24/7"
            ... )
            >>> print(story['title'])
            'Deploy code_developer on GCP'
        """
        try:
            prompt = f"""Extract User Story from this input:

{user_input}

Respond ONLY in this exact XML format:
<user_story>
<role>system administrator</role>
<want>deploy code_developer on GCP</want>
<so_that>it runs 24/7 autonomously</so_that>
<title>Deploy code_developer on GCP</title>
</user_story>

If this is NOT a User Story (no clear feature request), respond with: NOT_A_USER_STORY

Remember:
- role: Who needs this (developer, user, admin, etc.)
- want: What they want (feature/capability)
- so_that: Why they want it (benefit/value)
- title: Short descriptive title (5-10 words)
"""

            logger.debug(f"Extracting User Story from: {user_input[:100]}...")

            if self.use_claude_cli:
                # Use Claude CLI
                result = self.cli_interface.execute_prompt(prompt)
                if not result.success:
                    raise Exception(result.error)
                content = result.content.strip()
            else:
                # Use Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text.strip()

            # Check if it's not a User Story
            if "NOT_A_USER_STORY" in content:
                logger.debug("Input is not a User Story")
                return None

            # Parse XML response
            role_match = re.search(r"<role>(.+?)</role>", content, re.DOTALL)
            want_match = re.search(r"<want>(.+?)</want>", content, re.DOTALL)
            so_that_match = re.search(r"<so_that>(.+?)</so_that>", content, re.DOTALL)
            title_match = re.search(r"<title>(.+?)</title>", content, re.DOTALL)

            if not all([role_match, want_match, so_that_match, title_match]):
                logger.warning("Failed to parse User Story XML")
                return None

            story = {
                "role": role_match.group(1).strip(),
                "want": want_match.group(1).strip(),
                "so_that": so_that_match.group(1).strip(),
                "title": title_match.group(1).strip(),
            }

            logger.info(f"Extracted User Story: {story['title']}")
            return story

        except Exception as e:
            logger.error(f"User Story extraction failed: {e}")
            return None

    def generate_prioritization_question(self, story1: Dict, story2: Dict) -> str:
        """Generate natural question asking user to prioritize between two stories.

        Args:
            story1: First User Story dict with keys: id, title, role, want, so_that, estimated_effort
            story2: Second User Story dict with same structure

        Returns:
            Natural language question for user to answer

        Example:
            >>> question = service.generate_prioritization_question(
            ...     {'id': 'US-001', 'title': 'Deploy on GCP', 'estimated_effort': '5-7 days'},
            ...     {'id': 'US-002', 'title': 'CSV Export', 'estimated_effort': '2-3 days'}
            ... )
            >>> print(question)
            Between these two User Stories, which is more urgent?
            ...
        """
        try:
            question = f"""
Between these two User Stories, which is more urgent for you?

**A) {story1.get('title', 'Story 1')}**
   As a: {story1.get('role', 'user')}
   I want: {story1.get('want', '...')}
   Estimated effort: {story1.get('estimated_effort', 'TBD')}

**B) {story2.get('title', 'Story 2')}**
   As a: {story2.get('role', 'user')}
   I want: {story2.get('want', '...')}
   Estimated effort: {story2.get('estimated_effort', 'TBD')}

Your business priorities will help me organize the roadmap effectively.
Type **A** or **B** to indicate which story is more important to complete first.
"""
            return question.strip()

        except Exception as e:
            logger.error(f"Failed to generate prioritization question: {e}")
            return "Which story is more important?"

    def analyze_user_story_impact(self, story: Dict, roadmap_summary: Dict, priorities: List[Dict]) -> str:
        """Analyze roadmap impact of adding a User Story.

        Uses Claude AI to analyze how adding a User Story would affect the roadmap.

        Args:
            story: User Story dict
            roadmap_summary: Current roadmap summary
            priorities: List of existing priorities

        Returns:
            Impact analysis as formatted markdown string

        Example:
            >>> analysis = service.analyze_user_story_impact(
            ...     story={'title': 'Deploy on GCP', 'want': 'deploy on GCP', ...},
            ...     roadmap_summary={'total': 9, 'completed': 3, ...},
            ...     priorities=[...]
            ... )
        """
        try:
            # Build context about current roadmap
            priorities_text = "\n".join([f"- {p['number']}: {p['title']} ({p['status']})" for p in priorities[:10]])

            prompt = f"""Analyze the roadmap impact of adding this User Story:

**New User Story:**
- Title: {story.get('title', 'Unknown')}
- As a: {story.get('role', 'user')}
- I want: {story.get('want', 'feature')}
- So that: {story.get('so_that', 'benefit')}
- Estimated effort: {story.get('estimated_effort', 'TBD')}

**Current Roadmap:**
Total priorities: {roadmap_summary.get('total', 0)}
Completed: {roadmap_summary.get('completed', 0)}
In Progress: {roadmap_summary.get('in_progress', 0)}
Planned: {roadmap_summary.get('planned', 0)}

**Existing Priorities:**
{priorities_text}

Analyze:
1. Which existing priority(ies) could this User Story fit into?
2. Would this require a new priority?
3. What priorities might be delayed if we add this?
4. What dependencies exist?
5. What are the risks?
6. What's your recommendation?

Provide a concise analysis in markdown format.
"""

            logger.debug(f"Analyzing roadmap impact for story: {story.get('title')}")

            if self.use_claude_cli:
                # Use Claude CLI
                result = self.cli_interface.execute_prompt(prompt)
                if not result.success:
                    raise Exception(result.error)
                analysis = result.content
            else:
                # Use Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )
                analysis = response.content[0].text

            logger.info("Roadmap impact analysis generated")
            return analysis

        except Exception as e:
            logger.error(f"Impact analysis failed: {e}")
            return f"Unable to analyze impact: {str(e)}"

    def check_available(self) -> bool:
        """Check if AI service is available.

        Returns:
            True if API key is configured and accessible

        Example:
            >>> if service.check_available():
            ...     print("AI service ready!")
        """
        try:
            if self.use_claude_cli:
                # Check if Claude CLI is available
                available = self.cli_interface.check_available()
                logger.info(f"Claude CLI service available: {available}")
                return available
            else:
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
