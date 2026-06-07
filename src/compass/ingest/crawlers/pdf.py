
import httpx
import io
from pypdf import PdfReader
async def crawl_pdf(url: str) -> str | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        reader = PdfReader(io.BytesIO(response.content))
        text = "\n".join(page.extract_text() for page in reader.pages)
    return text