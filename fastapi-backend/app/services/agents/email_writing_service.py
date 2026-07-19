"""
Email Writing Agent Service - Integrates with Groq API for email generation
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from app.core.config import settings

EMAIL_AGENT_NAME = "AI Client Hunt Outreach Email Specialist"

EMAIL_AGENT_SYSTEM_INSTRUCTIONS = """
You are AI Client Hunt Outreach Email Specialist. Your mission is to write highly compelling, personalized outreach emails that convert website audit findings into client meetings.

REQUIRED EMAIL FLOW & STRUCTURE (Follow this exact 4-step sequence):

STEP 1: Genuine Opening & Business Praise (Deep Personalization)
- Greet the prospect team using their exact Business Name.
- Sincerely praise their business, brand, or reputation in their specific Industry and Location (e.g. "Came across [Business Name] while researching top [Industry] providers in [Location] and love what you've built!").
- Mention [Business Name] explicitly right away.

STEP 2: Praise High-Scoring Strengths & Explain Customer Growth Benefits
- Identify the website metrics where their audit score is high (scores >= 3.5/5, such as Mobile Responsiveness, SEO, SSL Security, or Load Speed).
- Praise these specific strong points on [Business Name]'s site.
- EXPLAIN WHY THIS IS A HUGE ADVANTAGE FOR GETTING CUSTOMERS: Describe how these strengths build instant trust, keep mobile users engaged, or make it easy for local customers in their area to discover [Business Name].

STEP 3: Address Low-Scoring Pain Points & Business Impact
- Smoothly transition to the lower-scoring audit metrics (scores < 3.5/5, such as missing Social Links, slow Speed, or unoptimized Images).
- Frame these issues naturally as growth opportunities that might currently be costing [Business Name] potential bookings, orders, or phone calls.
- Explain what real customers experience (e.g., "when visitors can't easily find your social pages or wait for images, they might leave before reaching out").

STEP 4: Personalized CTA & Soft Offer
- Re-mention [Business Name] naturally.
- Offer a low-pressure, friendly consultation or quick tip sheet to fix these pain points and unlock more revenue.
- End with a casual, low-friction call to action question (e.g., "Would you be open to a quick 5-minute chat this week on how we can help [Business Name] turn more site visitors into loyal customers?").

DEEP PERSONALIZATION & TONE RULES:
- ALWAYS mention the [Business Name] 2-3 times naturally throughout the email body.
- Reference their exact Industry and Location whenever available.
- DO NOT list raw score numbers like "SEO score 4/5" or "SSL 5/5". Translate scores into natural conversational phrasing.
- Writing Style: Professional, warm, helpful, and 100% human-sounding.
- Keep formatting clean plain-text (short 2-3 sentence paragraphs with line breaks).

OUTPUT FORMAT:
SUBJECT LINE 1: [Personal + curiosity, mentioning business name]
SUBJECT LINE 2: [Benefit/Outcome focused]
SUBJECT LINE 3: [Short & direct]

EMAIL BODY:
[Complete email body following Steps 1-4]

PERSONALIZATION NOTE:
[Short note explaining why this angle was chosen]

SIGNATURE:
Best,
AI Client Hunt Team
"""


class EmailWritingAgent:
    """Agent that generates personalized outreach emails based on audit scores"""

    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY

    def _get_groq_client(self):
        """Get Groq client"""
        if not self.groq_api_key:
            raise Exception("Groq API key not configured. Set GROQ_API_KEY in environment.")
        from groq import Groq
        return Groq(api_key=self.groq_api_key)

    def _build_user_prompt(
        self,
        business_name: str,
        website_url: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        target_audience: Optional[str] = None,
        business_goal: Optional[str] = None,
        seo_score: float = 0.0,
        ssl_score: float = 0.0,
        load_speed_score: float = 0.0,
        responsiveness_score: float = 0.0,
        social_links_score: float = 0.0,
        image_alt_score: float = 0.0,
        specific_issues: Optional[List[str]] = None,
        additional_notes: Optional[str] = None,
    ) -> str:
        """Build the user prompt for email generation"""
        scores = {
            "SEO & Search Visibility": seo_score,
            "SSL Security & Trust": ssl_score,
            "Load Speed & Performance": load_speed_score,
            "Mobile Responsiveness": responsiveness_score,
            "Social Media Integration": social_links_score,
            "Image Optimization": image_alt_score,
        }

        high_strengths = [f"{k} ({v}/5)" for k, v in scores.items() if v >= 3.5]
        low_pain_points = [f"{k} ({v}/5)" for k, v in scores.items() if v < 3.5]

        prompt = (
            "Generate a deeply personalized outreach email following the 4-step structure:\n\n"
            "PROSPECT BUSINESS DETAILS:\n"
            f"- Business Name: {business_name}\n"
            f"- Website URL: {website_url}\n"
            f"- Industry: {industry or 'Local Business'}\n"
            f"- Location: {location or 'your area'}\n"
            f"- Target Audience: {target_audience or 'local customers'}\n"
            f"- Primary Business Goal: {business_goal or 'Attract and convert more customers'}\n\n"
            "AUDIT PERFORMANCE CATEGORIZATION:\n"
            f"- High-Scoring Strengths (>= 3.5): {', '.join(high_strengths) if high_strengths else 'Solid brand presence'}\n"
            f"- Low-Scoring Pain Points (< 3.5): {', '.join(low_pain_points) if low_pain_points else 'Minor conversion tweaks'}\n\n"
            "DETAILED AUDIT SCORES:\n"
            f"- SEO: {seo_score}/5\n"
            f"- SSL: {ssl_score}/5\n"
            f"- Load Speed: {load_speed_score}/5\n"
            f"- Responsiveness: {responsiveness_score}/5\n"
            f"- Social Links: {social_links_score}/5\n"
            f"- Image Alt Tags: {image_alt_score}/5\n"
        )

        if specific_issues:
            prompt += "\nSPECIFIC AUDIT FLAWS NOTED:\n"
            for issue in specific_issues:
                prompt += f"- {issue}\n"

        if additional_notes:
            prompt += f"\nADDITIONAL CONTEXT & INSTRUCTIONS:\n{additional_notes}\n"

        prompt += (
            "\nREMINDER OF INSTRUCTIONS:\n"
            "1. Praise the business & brand genuinely in Step 1 (mention business name).\n"
            "2. Compliment high-scoring areas and explain HOW they bring customer growth in Step 2.\n"
            "3. Address low-scoring pain points and their customer impact in Step 3.\n"
            "4. Re-mention the business name with a soft, low-pressure CTA in Step 4.\n"
            "5. Ensure Business Name is mentioned multiple times naturally.\n\n"
            "Format your response EXACTLY as:\n"
            "SUBJECT LINE 1: [subject]\n"
            "SUBJECT LINE 2: [subject]\n"
            "SUBJECT LINE 3: [subject]\n\n"
            "EMAIL BODY:\n"
            "[email content]\n\n"
            "PERSONALIZATION NOTE:\n"
            "[note for sender]\n"
        )

        return prompt

    def generate_email(
        self,
        business_name: str,
        website_url: str,
        seo_score: float = 0.0,
        ssl_score: float = 0.0,
        load_speed_score: float = 0.0,
        responsiveness_score: float = 0.0,
        social_links_score: float = 0.0,
        image_alt_score: float = 0.0,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        target_audience: Optional[str] = None,
        business_goal: Optional[str] = None,
        specific_issues: Optional[List[str]] = None,
        additional_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a personalized outreach email.

        Args:
            business_name: Name of the target business
            website_url: Business website URL
            *_score: Audit scores (0-5)
            industry: Business industry
            location: Business location
            target_audience: Business target customers
            business_goal: What the business wants to achieve
            specific_issues: List of specific issues found
            additional_notes: Any additional context
            
        Returns:
            Dictionary with subject_lines, email_body, personalization_note, word_count
        """
        client = self._get_groq_client()
        user_prompt = self._build_user_prompt(
            business_name=business_name,
            website_url=website_url,
            industry=industry,
            location=location,
            target_audience=target_audience,
            business_goal=business_goal,
            seo_score=seo_score,
            ssl_score=ssl_score,
            load_speed_score=load_speed_score,
            responsiveness_score=responsiveness_score,
            social_links_score=social_links_score,
            image_alt_score=image_alt_score,
            specific_issues=specific_issues,
            additional_notes=additional_notes,
        )

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": EMAIL_AGENT_SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": user_prompt},
                ],
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": EMAIL_AGENT_SYSTEM_INSTRUCTIONS},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                response_text = completion.choices[0].message.content
            except Exception as e2:
                raise Exception("Email generation failed: " + str(e) + ", Fallback: " + str(e2))

        return self._parse_response(response_text)

    def generate_reply(self, chat_history: List[Dict[str, str]], prompt_instruction: str) -> str:
        """
        Generate an email reply based on the conversation history and a user prompt.
        """
        client = self._get_groq_client()
        
        system_instruction = (
            "You are AI Client Hunt Outreach Email Specialist. "
            "Write a reply to the prospect based on the conversation history. "
            "Follow the user's exact instruction for this reply. "
            "Return ONLY the plain text email body. DO NOT include subject lines, headers, or any conversational wrapper. "
            "Keep it casual, friendly, plain-text without markdown, and concise."
        )

        messages = [{"role": "system", "content": system_instruction}]
        
        # Format chat history
        history_text = "CONVERSATION HISTORY:\n\n"
        for msg in chat_history[-6:]:  # Last 6 messages for context
            sender = "Me (AI Client Hunt)" if msg.get("direction") == "outbound" else "Prospect"
            history_text += f"From: {sender}\nMessage:\n{msg.get('body', '')}\n\n---\n\n"
            
        messages.append({"role": "user", "content": history_text})
        messages.append({"role": "user", "content": f"Write a reply based on this instruction: {prompt_instruction}\n\nProvide ONLY the final email body text."})

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                )
                return completion.choices[0].message.content.strip()
            except Exception as e2:
                raise Exception(f"Reply generation failed: {e}, Fallback: {e2}")

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response to extract structured data"""
        result = {
            "subject_lines": [],
            "email_body": "",
            "personalization_note": "",
            "word_count": 0,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Extract subject lines
        subject_patterns = (
            r"SUBJECT LINE 1:\s*(.+)",
            r"SUBJECT LINE 2:\s*(.+)",
            r"SUBJECT LINE 3:\s*(.+)",
        )
        for pattern in subject_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                subject = match.group(1).strip().strip("\"'")
                result["subject_lines"].append(subject)

        # Extract email body
        body_match = re.search(
            r"EMAIL BODY:\s*(.+?)(?=PERSONALIZATION NOTE:|$)",
            response_text,
            re.DOTALL | re.IGNORECASE,
        )
        if body_match:
            result["email_body"] = body_match.group(1).strip()
        else:
            # Fallback: try to extract body between known markers
            lines = response_text.split("\n")
            email_start = False
            email_lines = []
            for line in lines:
                if "EMAIL BODY" in line.upper():
                    email_start = True
                    continue
                if "PERSONALIZATION NOTE" in line.upper():
                    email_start = False
                    continue
                if email_start:
                    email_lines.append(line)
            result["email_body"] = "\n".join(email_lines).strip()

        # Extract personalization note
        note_match = re.search(
            r"PERSONALIZATION NOTE:\s*(.+?)$",
            response_text,
            re.DOTALL | re.IGNORECASE,
        )
        if note_match:
            result["personalization_note"] = note_match.group(1).strip()

        # Word count
        result["word_count"] = len(result["email_body"].split())

        return result

    def generate_email_from_audit_and_business_data(
        self, audit_data: Dict[str, Any], business_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate email using combined audit and business data.

        Args:
            audit_data: Website audit results
            business_data: Extracted business information
            
        Returns:
            Generated email data
        """
        scores = audit_data.get("scores", {})
        specific_issues = []
        details = audit_data.get("details", {})
        for category, data in details.items():
            if isinstance(data, dict):
                flaws = data.get("flaws", [])
                specific_issues.extend(flaws)

        return self.generate_email(
            business_name=business_data.get("business_name", "Unknown Business"),
            website_url=business_data.get("website_url", ""),
            seo_score=scores.get("seo", 0.0),
            ssl_score=scores.get("ssl", 0.0),
            load_speed_score=scores.get("load_speed", 0.0),
            responsiveness_score=scores.get("responsiveness", 0.0),
            social_links_score=scores.get("social_links", 0.0),
            image_alt_score=scores.get("image_alt", 0.0),
            industry=business_data.get("industry", None),
            location=business_data.get("location", None),
            target_audience=business_data.get("target_audience", None),
            specific_issues=specific_issues,
        )
