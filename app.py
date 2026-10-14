import os
import re
from typing import List, Tuple
from dotenv import load_dotenv
import requests
import streamlit as st

load_dotenv()


def validate_inputs(topic: str, platforms: List[str], tone: str, length: str, include_emojis: bool, custom_prompt: str) -> Tuple[bool, str]:
    if not topic or not topic.strip():
        return False, "Please enter a topic, product, service, or content idea."
    if not platforms:
        return False, "Please select at least one platform."
    if not tone:
        return False, "Please select a tone."
    if not length:
        return False, "Please select a caption length."
    if custom_prompt and len(custom_prompt.strip()) < 5:
        return False, "Custom prompt is too short. Please provide a more detailed prompt."
    return True, ""


def build_prompt(topic: str, platforms: List[str], tone: str, length: str, include_emojis: bool, custom_prompt: str) -> str:
    platform_text = ", ".join(platforms)
    emoji_text = "include emojis" if include_emojis else "avoid emojis"
    length_guidance = {
        "short": "Write a concise caption with 1-2 sentences.",
        "medium": "Write a moderately detailed caption with 2-3 sentences.",
        "long": "Write a detailed caption with 3-5 sentences.",
    }
    base_prompt = (
        f"Create social media content for the topic: {topic}. "
        f"Target platforms: {platform_text}. "
        f"Tone: {tone}. "
        f"{length_guidance[length]} "
        f"{emoji_text}. "
        "Make it engaging, readable, and suitable for social media."
    )
    if custom_prompt.strip():
        return f"{base_prompt} Additional instructions: {custom_prompt.strip()}"
    return base_prompt


def generate_ai_caption(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a social media marketing assistant that creates concise, polished captions.",
                    },
                    {"role": "user", "content": f"Create one strong social media caption for this prompt: {prompt}"},
                ],
                "temperature": 0.8,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def build_fallback_caption(topic: str, platforms: List[str], tone: str, length: str, include_emojis: bool, index: int) -> str:
    platform_text = ", ".join(platforms)
    emoji = " ✨" if include_emojis else ""

    if length == "short":
        return f"{topic} is here to help you level up your workflow. Designed for {platform_text} in a {tone.lower()} style.{emoji}"

    if length == "medium":
        return (
            f"{topic} helps modern teams stay productive with smarter workflows and intuitive tools. "
            f"This caption is tailored for {platform_text}, keeping a {tone.lower()} tone while highlighting the main benefit: simplicity without sacrificing power.\n\n"
            f"It speaks directly to your audience’s need for efficiency, showing how {topic} saves time and reduces friction. "
            f"The message stays clear and engaging across the platform.\n\n"
            f"Wrap up with an inviting call-to-action that encourages readers to learn more and see how {topic} can improve their day.{emoji}"
        )

    return (
        f"{topic} offers a smarter way to get work done, combining elegant design with practical performance for {platform_text}. "
        f"It speaks to professionals who want clear results and fewer manual tasks.\n\n"
        f"In the next section, highlight the core value proposition: improved productivity, better collaboration, and more focus on what matters most. "
        f"Use {topic} as the dependable choice for ambitious teams and thoughtful creators.\n\n"
        f"Then add a user-centered example or benefit, such as faster decision-making, smoother scheduling, or cleaner workflows. "
        f"This keeps the caption grounded in real outcomes.\n\n"
        f"Continue with a reassuring statement about the product’s reliability and the way it fits modern social media audiences. "
        f"Maintain the {tone.lower()} voice while staying warm and professional.\n\n"
        f"Finish with a strong call-to-action that invites the reader to explore {topic} today and discover why it’s the right choice for their next campaign.{emoji}"
    )


def generate_variations(topic: str, platforms: List[str], tone: str, length: str, include_emojis: bool, custom_prompt: str, count: int = 3) -> List[dict]:
    prompt = build_prompt(topic, platforms, tone, length, include_emojis, custom_prompt)
    variations = []
    for index in range(1, count + 1):
        ai_caption = generate_ai_caption(prompt)
        caption = ai_caption or build_fallback_caption(topic, platforms, tone, length, include_emojis, index)
        hashtags = generate_hashtags(topic, platforms)
        variation = {
            "title": f"Content Variation {index}",
            "caption": caption,
            "hashtags": hashtags,
            "prompt": prompt,
        }
        variations.append(variation)
    return variations


def generate_hashtags(topic: str, platforms: List[str]) -> str:
    topic_words = re.findall(r"[A-Za-z0-9]+", topic)
    topic_slug = "".join(word.capitalize() for word in topic_words[:4]) if topic_words else "SocialMedia"
    base_tags = [f"#{topic_slug}"]
    related_tags = []

    for platform in platforms:
        related_tags.append(platform.lower().replace("/", "").replace(" ", ""))

    for word in topic_words[1:5]:
        if len(related_tags) + len(base_tags) >= 5:
            break
        normalized = word.lower()
        if normalized not in related_tags and normalized != topic_slug.lower():
            related_tags.append(normalized)

    while len(base_tags) + len(related_tags) < 5:
        related_tags.append("contentmarketing")

    all_tags = base_tags + [f"#{tag}" for tag in related_tags[:4]]
    return " ".join(all_tags)


def format_content(variation: dict) -> str:
    return f"{variation['caption']}\n\n{variation['hashtags']}"


st.set_page_config(page_title="Social Media Content Generator", page_icon="📱", layout="wide")

st.title("📱 Social Media Content Generator")
st.caption("Generate platform-aware captions, hashtags, and content variations from a simple prompt.")
st.caption("If OPENAI_API_KEY is set, the app will use OpenAI for richer captions; otherwise it uses built-in prompt-based generation.")

with st.sidebar:
    st.header("Generator Settings")
    topic = st.text_input("Topic / Product / Idea", placeholder="e.g. AI productivity app")
    platforms = st.multiselect(
        "Select Platforms",
        ["Instagram", "LinkedIn", "Facebook", "Twitter/X"],
        default=["Instagram"],
    )
    tone = st.selectbox("Tone", ["Professional", "Casual", "Promotional", "Informative", "Humorous"], index=0)
    length = st.selectbox("Caption Length", ["short", "medium", "long"], index=1)
    include_emojis = st.checkbox("Include emojis", value=True)
    custom_prompt = st.text_area("Custom Prompt Instructions", placeholder="Optional: add style, CTA, audience, or brand rules")
    generate_button = st.button("Generate Content", type="primary")
    regenerate_button = st.button("Regenerate")

st.subheader("Input Summary")
st.info("Provide a topic and platform choices to generate fresh social media content variations.")

if generate_button or regenerate_button:
    is_valid, message = validate_inputs(topic, platforms, tone, length, include_emojis, custom_prompt)
    if not is_valid:
        st.error(message)
    else:
        with st.spinner("Generating content variations..."):
            variations = generate_variations(topic, platforms, tone, length, include_emojis, custom_prompt)
        st.success("Content generated successfully.")
        tab_names = [f"Variation {index}" for index in range(1, len(variations) + 1)]
        tabs = st.tabs(tab_names)
        for idx, variation in enumerate(variations):
            with tabs[idx]:
                st.markdown(f"### {variation['title']}")
                st.write(variation['caption'])
                st.write(variation['hashtags'])
                st.text_area("Prompt Used", variation['prompt'], height=120, key=f"prompt_used_{idx}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Copy {idx + 1}", key=f"copy_{idx}"):
                        st.toast(f"Copied variation {idx + 1}")
                with col2:
                    content_text = format_content(variation)
                    st.download_button(
                        label=f"Download Variation {idx + 1}",
                        data=content_text,
                        file_name=f"social_content_{idx + 1}.txt",
                        mime="text/plain",
                        key=f"download_{idx}",
                    )

st.markdown("---")
st.subheader("How it works")
st.markdown(
    "- Enter a topic, product, or service idea.\n"
    "- Choose one or more platforms and a tone.\n"
    "- Optionally add custom instructions and generate multiple variations."
)
