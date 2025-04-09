"""
Notion Integration Utility for Beacon

This module provides functions to interact with Notion pages,
allowing access to information stored in Notion for the Beacon chatbot.
"""

import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.environ.get("NOTION_API_KEY"))


class NotionIntegration:
    def __init__(self, page_id: Optional[str] = None):
        """
        Initialize the Notion integration.
        
        Args:
            page_id: The ID of the Notion page to access. If not provided, 
                    will use the NOTION_PAGE_ID environment variable.
        """
        self.page_id = page_id or os.environ.get("NOTION_PAGE_ID")
        if not self.page_id:
            raise ValueError("Notion page ID not provided and not found in environment")

    def get_page_content(self, page_id: Optional[str] = None) -> Dict:
        """
        Get the content of a specific Notion page.
        
        Args:
            page_id: The ID of the Notion page. If not provided, uses the default page ID.
            
        Returns:
            Dict containing the page content
        """
        target_id = page_id or self.page_id
        return notion.pages.retrieve(page_id=target_id)
    
    def get_block_children(self, block_id: str, page_size: int = 100) -> Dict:
        """
        Get the children blocks of a specific block.
        
        Args:
            block_id: The ID of the block
            page_size: Number of children to retrieve
            
        Returns:
            Dict containing the children blocks
        """
        return notion.blocks.children.list(block_id=block_id, page_size=page_size)
    
    def extract_page_text(self, page_id: Optional[str] = None) -> str:
        """
        Extract text content from a Notion page.
        
        Args:
            page_id: The ID of the Notion page. If not provided, uses the default page ID.
            
        Returns:
            Extracted text content
        """
        target_id = page_id or self.page_id
        blocks = self.get_block_children(target_id)
        text_content = []
        
        for block in blocks.get("results", []):
            text = self._extract_text_from_block(block)
            if text:
                text_content.append(text)
                
        return "\n\n".join(text_content)
    
    def _extract_text_from_block(self, block: Dict) -> Optional[str]:
        """
        Extract text from a single block.
        
        Args:
            block: Notion block object
            
        Returns:
            Extracted text or None if no text is found
        """
        block_type = block.get("type")
        if not block_type:
            return None
        
        block_content = block.get(block_type, {})
        
        if block_type == "paragraph":
            return self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "heading_1":
            return "# " + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "heading_2":
            return "## " + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "heading_3":
            return "### " + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "bulleted_list_item":
            return "• " + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "numbered_list_item":
            return "1. " + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "to_do":
            checked = "✓ " if block_content.get("checked") else "☐ "
            return checked + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "code":
            language = block_content.get("language", "")
            code = self._extract_rich_text(block_content.get("rich_text", []))
            return f"```{language}\n{code}\n```"
        elif block_type == "quote":
            return "> " + self._extract_rich_text(block_content.get("rich_text", []))
        elif block_type == "image":
            caption = self._extract_rich_text(block_content.get("caption", []))
            return f"[Image: {caption if caption else 'No caption'}]"
        elif block_type == "divider":
            return "---"
        elif block_type == "callout":
            text = self._extract_rich_text(block_content.get("rich_text", []))
            emoji = block_content.get("icon", {}).get("emoji", "")
            return f"{emoji} {text}"
        
        return None
    
    def _extract_rich_text(self, rich_text: List[Dict]) -> str:
        """
        Extract plain text from rich text objects.
        
        Args:
            rich_text: List of rich text objects
            
        Returns:
            Extracted plain text
        """
        return "".join([text.get("plain_text", "") for text in rich_text])
    
    def search_in_notion(self, query: str) -> List[Dict]:
        """
        Search Notion for content matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results
        """
        response = notion.search(query=query)
        return response.get("results", [])
    
    def get_page_title(self, page_id: Optional[str] = None) -> str:
        """
        Get the title of a Notion page.
        
        Args:
            page_id: The ID of the Notion page. If not provided, uses the default page ID.
            
        Returns:
            Page title as string
        """
        target_id = page_id or self.page_id
        page = self.get_page_content(target_id)
        
        title = "Untitled"
        if "properties" in page and "title" in page["properties"]:
            title_elements = page["properties"]["title"].get("title", [])
            if title_elements:
                title = "".join([text.get("plain_text", "") for text in title_elements])
        
        return title
    
    def get_knowledge_base(self) -> Dict[str, str]:
        """
        Get the content of the Notion page as a knowledge base.
        
        Returns:
            Dict mapping page title to its content
        """
        title = self.get_page_title()
        content = self.extract_page_text()
        
        return {title: content}


def get_notion_content(page_id: Optional[str] = None) -> Dict[str, str]:
    """
    Helper function to get content from a Notion page.
    
    Args:
        page_id: Optional override for the page ID
        
    Returns:
        Dict mapping page title to its content
    """
    notion_integration = NotionIntegration(page_id)
    return notion_integration.get_knowledge_base() 