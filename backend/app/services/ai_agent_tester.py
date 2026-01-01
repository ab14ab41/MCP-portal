"""
AI Agent Testing Service - Test deployed MCP servers with AI agents (Anthropic & OpenAI-compatible).
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Literal
from anthropic import Anthropic
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class AIAgentTesterService:
    """Service for testing MCP servers with AI agents (Anthropic or OpenAI-compatible)."""

    def __init__(self):
        """Initialize AI agent tester service."""
        self.anthropic_client = None
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(
                api_key=settings.anthropic_api_key,
                default_headers={"anthropic-version": "2023-06-01"}
            )

        self.openai_client = None
        if settings.openai_api_key:
            self.openai_client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url
            )

    async def test_mcp_with_claude(
        self,
        server_id: str,
        server_name: str,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        mcp_tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test an MCP server by having Claude use its tools.

        Args:
            server_id: The ID of the deployed MCP server
            server_name: The name of the MCP server
            message: User's message to Claude
            conversation_history: Previous conversation messages
            mcp_tools: List of available MCP tools
            model: Optional model override (default: claude-3-haiku-20240307)
            api_key: Optional API key override

        Returns:
            Dict with response text, tool calls, and updated conversation history
        """
        # Use provided API key or fall back to configured client
        client = self.anthropic_client
        if api_key:
            client = Anthropic(
                api_key=api_key,
                default_headers={"anthropic-version": "2023-06-01"}
            )

        if not client and not api_key:
            raise ValueError("Anthropic API key not configured. Please set ANTHROPIC_API_KEY in environment or provide api_key parameter.")

        # Build conversation messages
        messages = conversation_history or []
        messages.append({
            "role": "user",
            "content": message
        })

        # Use provided model or default
        model_name = model or "claude-3-haiku-20240307"

        try:
            # Call Claude with the MCP tools
            response = client.messages.create(
                model=model_name,
                max_tokens=4096,
                tools=mcp_tools or [],
                messages=messages
            )

            # Extract response content
            response_text = ""
            tool_calls = []
            content_blocks = []

            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                    content_blocks.append({
                        "type": "text",
                        "text": block.text
                    })
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                    content_blocks.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

            # Add assistant's response to conversation
            messages.append({
                "role": "assistant",
                "content": content_blocks
            })

            result = {
                "response": response_text,
                "tool_calls": tool_calls,
                "conversation_history": messages,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

            # If Claude used tools, we need to execute them and continue the conversation
            if tool_calls and response.stop_reason == "tool_use":
                logger.info(f"Claude used {len(tool_calls)} tool(s): {[tc['name'] for tc in tool_calls]}")
                result["requires_tool_execution"] = True

            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error testing MCP with Claude: {error_msg}")

            # Provide helpful error messages
            if "not_found_error" in error_msg and "model:" in error_msg:
                raise ValueError(
                    "The specified Claude model was not found. This usually means:\n"
                    "1. Your API key doesn't have access to this model\n"
                    "2. Billing isn't set up in your Anthropic account\n"
                    "3. The API key needs to be activated\n\n"
                    "Please check: https://console.anthropic.com/settings/keys"
                )
            raise

    async def execute_tool_and_continue(
        self,
        server_id: str,
        tool_call: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        mcp_tools: List[Dict[str, Any]],
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call and get Claude's final response.

        Args:
            server_id: The ID of the deployed MCP server
            tool_call: The tool call to execute
            conversation_history: Current conversation history
            mcp_tools: List of available MCP tools
            model: Optional model override (default: claude-3-haiku-20240307)
            api_key: Optional API key override

        Returns:
            Dict with final response after tool execution
        """
        # Use provided API key or fall back to configured client
        client = self.anthropic_client
        if api_key:
            client = Anthropic(
                api_key=api_key,
                default_headers={"anthropic-version": "2023-06-01"}
            )

        if not client and not api_key:
            raise ValueError("Anthropic API key not configured")

        # Use provided model or default
        model_name = model or "claude-3-haiku-20240307"

        try:
            # Import the serving service to execute the tool
            from app.services.mcp_serving import mcp_serving_service

            # Execute the MCP tool
            tool_result = await mcp_serving_service.call_mcp_tool(
                server_id=server_id,
                tool_name=tool_call["name"],
                arguments=tool_call["input"]
            )

            # Add tool result to conversation
            conversation_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
                    }
                ]
            })

            # Get Claude's final response
            response = client.messages.create(
                model=model_name,
                max_tokens=4096,
                tools=mcp_tools,
                messages=conversation_history
            )

            # Extract final response
            response_text = ""
            additional_tool_calls = []
            content_blocks = []

            for block in response.content:
                if block.type == "text":
                    response_text += block.text
                    content_blocks.append({
                        "type": "text",
                        "text": block.text
                    })
                elif block.type == "tool_use":
                    additional_tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                    content_blocks.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

            # Add final response to conversation
            conversation_history.append({
                "role": "assistant",
                "content": content_blocks
            })

            return {
                "response": response_text,
                "tool_execution_result": tool_result,
                "additional_tool_calls": additional_tool_calls,
                "conversation_history": conversation_history,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error executing tool and continuing: {e}")
            raise

    def _convert_mcp_tools_to_openai_functions(self, mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert MCP tool schemas to OpenAI function calling format.

        Args:
            mcp_tools: List of MCP tool schemas (Anthropic format)

        Returns:
            List of OpenAI function schemas
        """
        openai_functions = []
        for tool in mcp_tools:
            openai_function = {
                "type": "function",
                "function": {
                    "name": tool.get("name"),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {})
                }
            }
            openai_functions.append(openai_function)
        return openai_functions

    async def test_mcp_with_openai(
        self,
        server_id: str,
        server_name: str,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        mcp_tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Test an MCP server by having an OpenAI-compatible model use its tools.

        Args:
            server_id: The ID of the deployed MCP server
            server_name: The name of the MCP server
            message: User's message to the model
            conversation_history: Previous conversation messages (OpenAI format)
            mcp_tools: List of available MCP tools (Anthropic format)
            model: Model name to use
            api_key: Optional API key override
            base_url: Optional base URL override

        Returns:
            Dict with response text, tool calls, and updated conversation history
        """
        # Use provided credentials or fall back to settings
        client = self.openai_client
        if api_key or base_url:
            client = OpenAI(
                api_key=api_key or settings.openai_api_key,
                base_url=base_url or settings.openai_base_url
            )

        if not client and not (api_key or self.openai_client):
            raise ValueError("OpenAI API key not configured. Please provide api_key parameter or set OPENAI_API_KEY in environment.")

        # Convert MCP tools to OpenAI function format
        openai_functions = self._convert_mcp_tools_to_openai_functions(mcp_tools or [])

        # Build conversation messages in OpenAI format
        messages = conversation_history or []
        messages.append({
            "role": "user",
            "content": message
        })

        try:
            # Call OpenAI with the functions
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=openai_functions if openai_functions else None,
                max_tokens=4096
            )

            # Extract response content
            choice = response.choices[0]
            message_obj = choice.message
            response_text = message_obj.content or ""
            tool_calls = []

            # Extract tool calls if any
            if message_obj.tool_calls:
                for tool_call in message_obj.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "input": json.loads(tool_call.function.arguments)
                    })

            # Add assistant's response to conversation
            assistant_message = {
                "role": "assistant",
                "content": response_text
            }
            if message_obj.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message_obj.tool_calls
                ]
            messages.append(assistant_message)

            result = {
                "response": response_text,
                "tool_calls": tool_calls,
                "conversation_history": messages,
                "stop_reason": choice.finish_reason,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0
                }
            }

            # If model used tools, we need to execute them and continue the conversation
            if tool_calls and choice.finish_reason == "tool_calls":
                logger.info(f"OpenAI model used {len(tool_calls)} tool(s): {[tc['name'] for tc in tool_calls]}")
                result["requires_tool_execution"] = True

            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error testing MCP with OpenAI: {error_msg}")
            raise

    async def execute_tool_and_continue_openai(
        self,
        server_id: str,
        tool_call: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        mcp_tools: List[Dict[str, Any]],
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call and get OpenAI model's final response.

        Args:
            server_id: The ID of the deployed MCP server
            tool_call: The tool call to execute
            conversation_history: Current conversation history (OpenAI format)
            mcp_tools: List of available MCP tools
            model: Model name to use
            api_key: Optional API key override
            base_url: Optional base URL override

        Returns:
            Dict with final response after tool execution
        """
        # Use provided credentials or fall back to settings
        client = self.openai_client
        if api_key or base_url:
            client = OpenAI(
                api_key=api_key or settings.openai_api_key,
                base_url=base_url or settings.openai_base_url
            )

        if not client and not (api_key or self.openai_client):
            raise ValueError("OpenAI API key not configured")

        try:
            # Import the serving service to execute the tool
            from app.services.mcp_serving import mcp_serving_service

            # Execute the MCP tool
            tool_result = await mcp_serving_service.call_mcp_tool(
                server_id=server_id,
                tool_name=tool_call["name"],
                arguments=tool_call["input"]
            )

            # Add tool result to conversation (OpenAI format)
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
            })

            # Convert MCP tools to OpenAI function format
            openai_functions = self._convert_mcp_tools_to_openai_functions(mcp_tools)

            # Get model's final response
            response = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                tools=openai_functions if openai_functions else None,
                max_tokens=4096
            )

            # Extract final response
            choice = response.choices[0]
            message_obj = choice.message
            response_text = message_obj.content or ""
            additional_tool_calls = []

            # Extract additional tool calls if any
            if message_obj.tool_calls:
                for tool_call_obj in message_obj.tool_calls:
                    additional_tool_calls.append({
                        "id": tool_call_obj.id,
                        "name": tool_call_obj.function.name,
                        "input": json.loads(tool_call_obj.function.arguments)
                    })

            # Add final response to conversation
            assistant_message = {
                "role": "assistant",
                "content": response_text
            }
            if message_obj.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message_obj.tool_calls
                ]
            conversation_history.append(assistant_message)

            return {
                "response": response_text,
                "tool_execution_result": tool_result,
                "additional_tool_calls": additional_tool_calls,
                "conversation_history": conversation_history,
                "stop_reason": choice.finish_reason,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0
                }
            }

        except Exception as e:
            logger.error(f"Error executing tool and continuing with OpenAI: {e}")
            raise


# Global service instance
ai_agent_tester_service = AIAgentTesterService()
