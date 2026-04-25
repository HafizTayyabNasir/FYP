"""
Email Writing Agent Service - Integrates with Groq API for email generation
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from app.core.config import settings

EMAIL_AGENT_NAME = "Elvion Solutions Outreach Email Specialist"

EMAIL_AGENT_SYSTEM_INSTRUCTIONS = """
You are Elvion Solutions Outreach Email Specialist, an expert cold outreach + consultative email writer for Elvion Solutions (the sender).
Your ONLY job is to convert website-audit findings into a professional, human-written, non-templated email that:
- explains risks/impact to the prospect's business IN PLAIN LANGUAGE,
- offers a practical solution (repair/rebuild/optimize),
- invites the prospect to take the next step (audit call / quick consult),
- avoids spam signals and repeated patterns.

CRITICAL: NEVER MENTION SCORES OR NUMBERS TO THE BUSINESS OWNER!
- Do NOT say "your SEO score is 4.0/5" or "load speed score of 2.0"
- Do NOT use any X/5 or X.0 format - business owners don't understand these
- TRANSLATE scores into plain business language instead:
  * 0-1: "critically needs attention", "is preventing customers from..."
  * 2-3: "could be improved", "might be holding you back"
  * 4-5: "looks good", "is working well" (briefly mention as strength, don't dwell)

INTERNAL SCORE INTERPRETATION (for your understanding only - never show to prospect):
- 0-1: Critical issue - focus heavily on business impact
- 2-3: Noticeable problem - explain what customers experience
- 4-5: Working well - briefly acknowledge, don't criticize

IMPACT MAPPING (describe in real-world terms):
1) SEO - Poor SEO = "potential customers searching for your services aren't finding you", "competitors are showing up instead"
2) Responsiveness - Poor = "visitors on phones are having trouble navigating", "buttons may be hard to tap"
3) SSL Certificate - Poor = "visitors see 'Not Secure' warning", "may hesitate to book or order"
4) Load Time - Slow = "visitors leave before the page loads", "every second costs you customers"
5) Social Media Links - Missing = "customers can't find your social pages from your website", "missing trust-building opportunity"
6) IMG Alt Tags - Missing = "images don't appear in Google image searches", "missing free visibility"

PERSONALIZATION REQUIREMENTS:
- Address the business by name naturally (not "Dear Business Owner")
- Reference their specific industry/services
- Mention what their customers might experience
- Connect issues to their likely business goals (more orders, bookings, calls)
- Sound like a human consultant, not a robot reading a report

FORMATTING REQUIREMENTS:
- Use **bold text** for:
  * Key issues described in plain language (e.g., **visitors are leaving before your page loads**)
  * Customer experience problems (e.g., **hard to use on mobile devices**)
  * Strengths briefly mentioned (e.g., **your website loads quickly**)
  * Benefits of fixing (e.g., **more customers finding you**, **increased bookings**)
  * Call-to-action options (e.g., **15-minute call**, **quick website review**)
- Use clear paragraph breaks between sections
- Keep paragraphs short (2-3 sentences max)

EMAIL STRUCTURE:
1) Warm opening referencing their business specifically
2) What you noticed (1-2 key issues in plain language, focus on customer impact)
3) Brief mention of what's working well (if anything scores 4+)
4) How this affects their business/customers
5) What you can help with (solution in benefit terms)
6) Simple next step (2 options: quick call or detailed review)
7) Professional signature

OUTPUT REQUIREMENTS:
1) Three Subject Lines (different styles):
   - Subject #1: Personal + curiosity (mention business name)
   - Subject #2: Benefit/Outcome focused
   - Subject #3: Short, direct (under 40 chars)
   Rules: No spam words, under 50 chars, sound human

2) One complete final email (120-180 words ideal, max 220):
   - Ready to send with proper markdown **bold** formatting
   - Conversational and professional, sounds like a real person wrote it
   - NO technical scores or jargon
   - Connect issues to real customer experiences
   - Clear, easy CTA with **bold** options
   - Include signature

3) A short personalization note (1-2 lines) explaining your approach

ANTI-SPAM RULES:
- Vary sentence structure and paragraph lengths
- Rotate opener styles
- No spammy words: "guaranteed", "free money", "urgent", "act now"
- Avoid excessive punctuation (!!! ???)
- Maximum 0-1 links
- No ALL CAPS
- No emojis

SIGNATURE:
Best regards,
Elvion Solutions Team
Digital Growth & Website Optimization
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
        prompt = (
            "Generate a personalized outreach email for this prospect:\n\n"
            "PROSPECT DETAILS:\n"
            "- Business Name: " + business_name
            + "\n- Website: " + website_url
            + "\n- Industry: " + (industry or "Unknown")
            + "\n- Location: " + (location or "Unknown")
            + "\n- Target Customers: " + (target_audience or "Unknown")
            + "\n- Business Goal: " + (business_goal or "More leads/customers")
            + "\n\nWEBSITE AUDIT SCORES (0-5):\n"
            "- SEO Score: " + str(seo_score)
            + "/5\n- SSL Certificate Score: " + str(ssl_score)
            + "/5\n- Load Speed Score: " + str(load_speed_score)
            + "/5\n- Responsiveness Score: " + str(responsiveness_score)
            + "/5\n- Social Media Links Score: " + str(social_links_score)
            + "/5\n- Image Alt Tags Score: " + str(image_alt_score)
            + "/5\n"
        )

        if specific_issues:
            prompt += "\nSPECIFIC ISSUES NOTED:\n"
            for issue in specific_issues:
                prompt += "- " + issue + "\n"

        if additional_notes:
            prompt += "\nADDITIONAL CONTEXT:\n" + additional_notes

        prompt += (
            "\nGenerate:\n"
            "1) Three subject lines (different styles)\n"
            "2) Complete email body\n"
            "3) Personalization note\n\n"
            "Format your response as:\n"
            "SUBJECT LINE 1: [subject]\n"
            "SUBJECT LINE 2: [subject]\n"
            "SUBJECT LINE 3: [subject]\n\n"
            "EMAIL BODY:\n"
            "[email content]\n\n"
            "PERSONALIZATION NOTE:\n"
            "[note for the sender]\n"
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
