import os
from notion_client import Client
from dotenv import load_dotenv
import json
from datetime import datetime

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

    def add_element(self, page_id: str, content_type: str, content_text: str) -> None:
        """ """
        element = [
            {
                "object": "block",
                "type": content_type,
                content_type: {
                    "rich_text": [{"type": "text", "text": {"content": content_text}}]
                },
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


# properties_to_update = {
#     "title": {"title": [{"text": {"content": "Finance News"}}]},
# }

# notion.pages.update(
#     _NOTION_PAGE_ID,
#     properties=properties_to_update,
# )


# subpages = get_subpages(notion)

# existing_blocks = notion.blocks.children.list(block_id=_NOTION_PAGE_ID).get("results")

# with open("notion_data.json", "w") as f:
#     json.dump(existing_blocks, f, indent=4)

# new_content = [
#     {
#         "object": "block",
#         "type": "paragraph",
#         "paragraph": {
#             "rich_text": [{"type": "text", "text": {"content": "This is a new paragraph."}}]
#         }
#     },
#     {
#         "object": "block",
#         "type": "heading_2",
#         "heading_2": {
#             "rich_text": [{"type": "text", "text": {"content": "This is a new heading"}}]
#         }
#     },
#     {
#         "object": "block",
#         "type": "bulleted_list_item",
#         "bulleted_list_item": {
#             "rich_text": [{"type": "text", "text": {"content": "This is a bullet point"}}]
#         }
#     }
# ]

# notion.blocks.children.append(
#     block_id=_NOTION_PAGE_ID,
#     children=new_content
# )

# print(existing_blocks)

# print(subpages)
# for subpage in subpages:
#     print(subpage["id"], subpage["properties"]["title"]["title"][0]["text"]["content"])
#     subpage_id = subpage["id"]
#     if subpage_id == _NOTION_PAGE_ID:
#         continue
#     subpage_title = subpage["properties"]["title"]["title"][0]["text"]["content"]

#     # Update the title of the subpage
#     properties_to_update = {
#         "title": {
#             "title": [{"text": {"content": f"{subpage_title} - Finance News Updated"}}]
#         },
#     }

#     notion.pages.update(
#         subpage_id,
#         properties=properties_to_update,
#     )

if __name__ == "__main__":
    notion = NotionClient()
    tickers_news = None
    today = datetime.today().strftime("%m-%d-%Y")
    print(today)
    # notion.delete_page(f"cde - Finance News")
