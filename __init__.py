from .prompt_library_node import PromptLibraryNode, PromptLibraryExtraNode

NODE_CLASS_MAPPINGS = {
    "PromptLibraryNode": PromptLibraryNode,
    "PromptLibraryExtraNode": PromptLibraryExtraNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptLibraryNode": "Prompt Library",
    "PromptLibraryExtraNode": "Prompt Library (Extra)",
}