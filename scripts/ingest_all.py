# Good. Now write the main ingestion script — scripts/ingest_all.py. This is the orchestrator that defines all your source URLs and calls ingest_url for each. Structure it as a list of tuples (url, source_type), then loop through and call ingest_url for each, printing progress.

# Start with just the Anthropic docs URLs — pick 5-8 pages covering prompt engineering, tool use, agents, and the overview you already have. We'll add the other sources after.
import asyncio
from compass.ingest.pipeline import ingest_url
from compass.config import Config

async def main():
    config = Config()
    urls = [
        ("https://platform.claude.com/llms-full.txt", "anthropic_docs"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/codex_exec_plans.md", "openai_cookbook"),
        ("http://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/gpt-oss-safeguard-guide.md", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/how_to_work_with_large_language_models.md", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/openai-harmony.md", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/related_resources.md", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/techniques_to_improve_reliability.md", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/text_comparison_examples.md", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/what_is_new_with_dalle_3.mdx", "openai_cookbook"),
        ("https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/articles/what_makes_documentation_good.md", "openai_cookbook"),
        ("https://arxiv.org/pdf/2005.11401.pdf", "arxiv_paper"),
        ("https://arxiv.org/pdf/2210.03629.pdf", "arxiv_paper"),
        ("https://arxiv.org/pdf/2212.08073.pdf", "arxiv_paper"),
        ("https://hamel.dev/blog/posts/evals/", "blog" ),
        ("https://huyenchip.com/2023/04/11/llm-engineering.html", "blog"),
        ("https://eugeneyan.com/writing/llm-patterns/", "blog"),
        ("https://lilianweng.github.io/posts/2023-06-23-agent/", "blog"),
        ("https://simonwillison.net/2025/Mar/11/using-llms-for-code/", "blog"),
        
         
        
        # Add more URLs here as needed
    ]
    for url, source_type in urls:
        print(f"Ingesting {url}...")
        num_chunks = await ingest_url(url, config, source_type)
        print(f"Ingested {num_chunks} chunks from {url}")
        
if __name__ == "__main__":
    asyncio.run(main())