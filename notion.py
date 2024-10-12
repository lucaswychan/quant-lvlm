import os
from notion_client import Client
from dotenv import load_dotenv
import json

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
        # create a new page object
        new_created_page = self._client.pages.create(
            parent={"page_id": self._main_page_id},
            properties={
                "title": [{"text": {"content": title}}]
            }
        )
        
        return new_created_page

    def add_element(self, page_id: str, content_type: str, content_text: str):
        element = [{
            "object": "block",
            "type": content_type,
            content_type: {
                "rich_text": [{"type": "text", "text": {"content": content_text}}]
            }
        }]
        self._client.blocks.children.append(
            block_id=page_id,
            children=element
        )
        
        
        

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
    new_page = notion.create_page("Finance News Sub Page")
    
    
    new_page_id = new_page["id"]
    
    notion.add_element(new_page_id, "paragraph", "This is a new paragraph.")
    notion.add_element(new_page_id, "heading_2", "This is a new heading")
    notion.add_element(new_page_id, "bulleted_list_item", "This is a bullet point")
