import json
import os
from datetime import datetime

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()


class NotionClient:
    def __init__(self):
        self._token = os.getenv("NOTION_TOKEN", "")
        if self._token == "":
            raise ValueError(
                "Please provide a valid NOTION_TOKEN in your environment variables."
            )

        self._main_page_id = os.getenv("NOTION_PAGE_ID", "")
        if self._main_page_id == "":
            raise ValueError(
                "Please provide a valid NOTION_PAGE_ID in your environment variables."
            )
        self._client = Client(auth=self._token)

    def create_page(self, title: str) -> dict:
        """
        Create a new page in the main page.
        """
        already_exists, page_id = self._check_subpage_exists(title)
        if already_exists:
            return self._client.pages.retrieve(page_id)

        new_created_page = self._client.pages.create(
            parent={"page_id": self._main_page_id},
            properties={"title": [{"text": {"content": title}}]},
        )

        return new_created_page

    def add_element(
        self,
        page_id: str,
        content_type: str,
        content_text: str,
        is_bold: bool = False,
        is_italic: bool = False,
        is_strikethrough: bool = False,
        is_underline: bool = False,
        is_code: bool = False,
        color: str = "default",
        link: str = None,
    ) -> None:
        """
        Add a new element to the page.
        """

        link_obj = {"url": link} if link is not None else None

        element = [
            {
                "object": "block",
                "type": content_type,
                content_type: {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": content_text, "link": link_obj},
                            "annotations": {
                                "bold": is_bold,
                                "italic": is_italic,
                                "strikethrough": is_strikethrough,
                                "underline": is_underline,
                                "code": is_code,
                                "color": color,
                            },
                        }
                    ]
                },
            }
        ]
        self._client.blocks.children.append(block_id=page_id, children=element)

    def add_multiple_elements(
        self, page_id: str, elements_to_be_added: list[dict]
    ) -> None:
        """
        Add multiple elements to the page.
        """

        for element in elements_to_be_added:
            self.add_element(page_id, **element)

    def add_new_line(self, page_id: str) -> None:
        """
        Add a new line to the page.
        """
        self.add_element(page_id, "paragraph", " ")

    def add_divider(self, page_id: str) -> None:
        """
        Add a new divider to the page.
        """
        element = [
            {
                "object": "block",
                "type": "divider",
                "divider": {},
            }
        ]
        self._client.blocks.children.append(block_id=page_id, children=element)

    def _check_subpage_exists(self, subpage_title) -> tuple[bool, str]:
        try:
            # Search for pages with the given title
            response = self._client.search(
                query=subpage_title, filter={"property": "object", "value": "page"}
            ).get("results")

            # Filter the results to find a page with matching parent and title
            for page in response:
                if (
                    page.get("parent", {}).get("type") == "page_id"
                    and page["parent"]["page_id"].replace("-", "") == self._main_page_id
                ):
                    # Check the title of the page
                    page_title = page["properties"].get("title", {}).get("title", [])
                    if page_title and page_title[0].get("plain_text") == subpage_title:
                        return True, page["id"]

            # If no matching page is found
            return False, None

        except Exception as e:
            print(f"An error occurred while checking for the subpage: {str(e)}")
            return False, None

    def delete_page(self, title: str) -> None:
        """
        Not really deleting the page, but archiving it.
        """
        self._client.pages.update(self._check_subpage_exists(title)[1], archived=True)


if __name__ == "__main__":
    notion = NotionClient()

    created_page = notion.create_page("Test Design")
    page_id = created_page["id"]

    elements = [
        {"content_type": "paragraph", "content_text": " "},
        {
            "content_type": "heading_2",
            "content_text": "Title 2: the title of the first news",
        },
        {"content_type": "paragraph", "content_text": "Got some conclusion !!!!"},
        {"content_type": "paragraph", "content_text": " "},
        {
            "content_type": "paragraph",
            "content_text": "Sentiment: negatice",
            "is_bold": True,
        },
        {
            "content_type": "paragraph",
            "content_text": "https://google.com",
            "link": "https://google.com",
        },
        {"content_type": "paragraph", "content_text": " "},
    ]

    for element in elements:
        notion.add_element(page_id, **element)

    # notion.add_space(page_id)

    # notion.add_element(page_id, "heading_2", "Title 1: the title of the first news")
    # notion.add_element(page_id, "paragraph", "Got some conclusion")
    # notion.add_space(page_id)
    # notion.add_element(page_id, "paragraph", "Sentiment: positive", is_bold=True)
    # notion.add_element(
    #     page_id, "paragraph", "https://google.com", link="https://google.com"
    # )
    # notion.add_space(page_id)

    notion.add_divider(page_id)
