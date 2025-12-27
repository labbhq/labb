from labb.llms import get_llms_txt


def display_llms_txt():
    """Display llms.txt content for AI/LLM consumption"""
    content = get_llms_txt()
    print(content)
