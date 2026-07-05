from app.services.email.resend_sender import send_email
from app.core.config import settings

def send_verification_email(email: str, token: str, frontend_url: str) -> bool:
    verify_url = f"{frontend_url}/verify-email?token={token}"
    
    subject = "Verify your email for AI Client Hunt"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #6D5DF6;">Welcome to AI Client Hunt!</h2>
        <p>Please click the button below to verify your email address. This link will expire in 24 hours.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_url}" style="background-color: #6D5DF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Verify Email</a>
        </div>
        <p style="color: #666; font-size: 14px;">If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="color: #666; font-size: 14px; word-break: break-all;">{verify_url}</p>
    </div>
    """
    
    result = send_email(
        to_email=email,
        subject=subject,
        body=f"Please verify your email: {verify_url}",
        html_body=html_body,
        from_email="noresponse@elvionsolutions.com"
    )
    
    return result.get("success", False)
