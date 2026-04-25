"""
Website Audit Orchestrator - Combines all audit modules
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from app.schemas.audit import (
    WebsiteAuditResponse,
    SEOAuditResult,
    SSLAuditResult,
    LoadSpeedAuditResult,
    ResponsivenessAuditResult,
    SocialLinksAuditResult,
    ImageAltAuditResult
)


class WebsiteAuditOrchestrator:
    """Orchestrates website audits across all modules"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=6)
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL to ensure it starts with https://"""
        url = url.strip()
        if not url:
            return ""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
    
    def run_audit(
        self,
        website_url: str,
        include_seo: bool = True,
        include_ssl: bool = True,
        include_speed: bool = True,
        include_responsiveness: bool = True,
        include_social_links: bool = True,
        include_image_alt: bool = True
    ) -> WebsiteAuditResponse:
        """
        Run a complete website audit.
        
        Args:
            website_url: URL to audit
            include_*: Flags to include specific audit types
            
        Returns:
            WebsiteAuditResponse with all audit results
        """
        url = self.normalize_url(website_url)
        
        results = {}
        futures = {}
        
        # Launch audit tasks in parallel
        if include_seo:
            futures['seo'] = self.executor.submit(self._audit_seo, url)
        if include_ssl:
            futures['ssl'] = self.executor.submit(self._audit_ssl, url)
        if include_speed:
            futures['speed'] = self.executor.submit(self._audit_speed, url)
        if include_responsiveness:
            futures['responsiveness'] = self.executor.submit(self._audit_responsiveness, url)
        if include_social_links:
            futures['social'] = self.executor.submit(self._audit_social_links, url)
        if include_image_alt:
            futures['image_alt'] = self.executor.submit(self._audit_image_alt, url)
        
        # Collect results
        for key, future in futures.items():
            try:
                results[key] = future.result(timeout=120)
            except Exception as e:
                results[key] = {"error": str(e), "score": 0}
        
        # Calculate overall score
        scores = []
        if 'seo' in results and isinstance(results['seo'], dict):
            scores.append(results['seo'].get('score', 0))
        if 'ssl' in results and isinstance(results['ssl'], dict):
            scores.append(results['ssl'].get('score', 0))
        if 'speed' in results and isinstance(results['speed'], dict):
            scores.append(results['speed'].get('score', 0))
        if 'responsiveness' in results and isinstance(results['responsiveness'], dict):
            scores.append(results['responsiveness'].get('score', 0))
        if 'social' in results and isinstance(results['social'], dict):
            scores.append(results['social'].get('score', 0))
        if 'image_alt' in results and isinstance(results['image_alt'], dict):
            scores.append(results['image_alt'].get('score', 0))
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Build response
        response = WebsiteAuditResponse(
            website_url=url,
            audit_timestamp=datetime.utcnow(),
            overall_score=round(overall_score, 2),
            seo=self._build_seo_result(results.get('seo')),
            ssl=self._build_ssl_result(results.get('ssl')),
            load_speed=self._build_speed_result(results.get('speed')),
            responsiveness=self._build_responsiveness_result(results.get('responsiveness')),
            social_links=self._build_social_result(results.get('social')),
            image_alt=self._build_image_alt_result(results.get('image_alt')),
            summary=self._generate_summary(results, overall_score),
            recommendations=self._generate_recommendations(results)
        )
        
        return response
    
    def _audit_seo(self, url: str) -> Dict[str, Any]:
        """Run SEO metadata audit"""
        try:
            from app.services.website_audit.modules.seo_metadata import (
                check_seo_metadata,
                rate_seo_metadata
            )
            metadata = check_seo_metadata(url)
            if metadata is None:
                return {"score": 0, "flaws": ["Could not fetch website"], "metadata": None}
            
            score, flaws = rate_seo_metadata(metadata)
            return {"score": score, "flaws": flaws, "metadata": metadata}
        except Exception as e:
            return {"score": 0, "flaws": [str(e)], "metadata": None}
    
    def _audit_ssl(self, url: str) -> Dict[str, Any]:
        """Run SSL certificate audit"""
        try:
            from app.services.website_audit.modules.ssl_certificate import (
                normalize_input_url,
                check_https_access,
                fetch_certificate,
                evaluate_certificate_dates,
                check_http_redirect,
                rate_ssl
            )
            
            host, http_url, https_url = normalize_input_url(url)
            if not host or not http_url or not https_url:
                return {"score": 0, "flaws": ["Invalid URL"]}
            
            flaws = []
            
            # Check HTTPS access
            https_ok, status_code, https_err = check_https_access(str(https_url))
            if not https_ok:
                flaws.append(f"HTTPS not accessible: {https_err}")
            
            # Check certificate
            cert_ok = False
            days_left = None
            cert, cert_err_type, cert_err_msg = fetch_certificate(host)
            
            if cert is None:
                if cert_err_type == "self_signed_certificate":
                    flaws.append("Self-signed certificate (not trusted)")
                elif cert_err_type == "certificate_expired":
                    flaws.append("Certificate expired")
                else:
                    flaws.append(f"Certificate error: {cert_err_type}")
            else:
                cert_ok, nb, na, days_left, cert_flaws = evaluate_certificate_dates(cert)
                flaws.extend(cert_flaws)
            
            # Check redirect
            redirects_https, final_url, first_code, hsts_present, redirect_flaws = check_http_redirect(str(http_url))
            flaws.extend(redirect_flaws)
            
            if https_ok and cert_ok and redirects_https and not hsts_present:
                flaws.append("HSTS header missing")
            
            score = rate_ssl(https_ok, cert_ok, days_left, redirects_https, hsts_present)
            
            return {
                "score": score,
                "flaws": flaws,
                "https_accessible": https_ok,
                "certificate_valid": cert_ok,
                "days_until_expiry": days_left,
                "hsts_enabled": hsts_present,
                "redirects_to_https": redirects_https
            }
        except Exception as e:
            return {"score": 0, "flaws": [str(e)]}
    
    def _audit_speed(self, url: str) -> Dict[str, Any]:
        """Run load speed audit - uses requests for faster basic check"""
        try:
            import time
            import requests
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            flaws = []
            
            # Measure response time with requests (fast)
            start = time.perf_counter()
            response = requests.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
            response_time_ms = (time.perf_counter() - start) * 1000
            
            # Get page size
            page_size = len(response.content)
            
            # Rate based on response time
            if response_time_ms < 1000:
                score = 5
            elif response_time_ms < 2000:
                score = 4
            elif response_time_ms < 3000:
                score = 3
            elif response_time_ms < 5000:
                score = 2
            elif response_time_ms < 8000:
                score = 1
            else:
                score = 0
            
            # Check for issues
            if response_time_ms > 3000:
                flaws.append(f"Slow server response: {response_time_ms:.0f}ms")
            if page_size > 3000000:  # > 3MB
                flaws.append(f"Large page size: {page_size / 1024 / 1024:.2f}MB")
            
            return {
                "score": score,
                "flaws": flaws,
                "load_time_ms": response_time_ms,
                "dom_content_loaded_ms": response_time_ms,
                "timing_details": {
                    "page_size": page_size,
                    "response_time_ms": response_time_ms
                }
            }
        except Exception as e:
            return {"score": 0, "flaws": [str(e)], "load_time_ms": None}
    
    def _audit_responsiveness(self, url: str) -> Dict[str, Any]:
        """Run responsiveness audit - uses requests to check viewport meta and media queries"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            flaws = []
            response = requests.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Check for viewport meta tag
            viewport_meta = soup.find("meta", attrs={"name": "viewport"})
            has_viewport = viewport_meta is not None
            
            # Check viewport content
            viewport_content = ""
            if has_viewport:
                viewport_content = str(viewport_meta.get("content", "") or "")
            
            # Check for responsive indicators
            has_width_device = "width=device-width" in viewport_content.lower().replace(" ", "")
            
            # Check for media queries in inline styles
            style_tags = soup.find_all("style")
            has_media_queries = False
            for style in style_tags:
                if style.string and "@media" in style.string:
                    has_media_queries = True
                    break
            
            # Check for responsive framework classes
            html_content = response.text.lower()
            has_bootstrap = "bootstrap" in html_content or "col-md-" in html_content or "col-lg-" in html_content
            has_tailwind = "tailwind" in html_content or "sm:" in html_content or "md:" in html_content
            has_responsive_classes = has_bootstrap or has_tailwind
            
            # Calculate score
            score = 0
            if has_viewport:
                score += 2
            else:
                flaws.append("Missing viewport meta tag")
            
            if has_width_device:
                score += 1
            else:
                flaws.append("Viewport doesn't set width=device-width")
            
            if has_media_queries or has_responsive_classes:
                score += 2
            else:
                flaws.append("No responsive CSS detected")
            
            score = min(score, 5)
            
            return {
                "score": score,
                "flaws": flaws,
                "pages_checked": 1,
                "viewport_meta_present": has_viewport,
                "has_media_queries": has_media_queries,
                "mobile_friendly": has_viewport and has_width_device
            }
        except Exception as e:
            return {"score": 0, "flaws": [str(e)], "pages_checked": 0}
    
    def _audit_social_links(self, url: str) -> Dict[str, Any]:
        """Run social links audit"""
        try:
            from app.services.website_audit.modules.social_links import (
                normalize_url,
                fetch_html,
                extract_social_links,
                check_with_requests,
                platform_name
            )
            
            url = normalize_url(url)
            html = fetch_html(url)
            links = extract_social_links(url, html)
            
            accessible = 0
            broken = 0
            platforms = []
            flaws = []
            
            for link in links[:10]:  # Limit to 10 links
                state, code, _ = check_with_requests(link)
                platform = platform_name(link)
                if platform not in platforms:
                    platforms.append(platform)
                
                if state == "WORKING":
                    accessible += 1
                else:
                    broken += 1
                    flaws.append(f"Broken {platform} link")
            
            found = len(links)
            
            # Calculate score
            if found == 0:
                score = 0
                flaws.append("No social media links found")
            elif broken > accessible:
                score = 1
            elif found < 3:
                score = 2
                flaws.append("Few social media links")
            elif broken > 0:
                score = 3
            else:
                score = 5 if found >= 4 else 4
            
            return {
                "score": score,
                "flaws": flaws,
                "links_found": found,
                "links_accessible": accessible,
                "links_broken": broken,
                "social_platforms": platforms
            }
        except Exception as e:
            return {"score": 0, "flaws": [str(e)], "links_found": 0}
    
    def _audit_image_alt(self, url: str) -> Dict[str, Any]:
        """Run image alt tags audit - uses requests and BeautifulSoup for speed"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            url = url.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            response = requests.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
            soup = BeautifulSoup(response.text, "html.parser")
            
            images = soup.find_all("img")
            total_images = len(images)
            images_without_alt = 0
            images_with_empty_alt = 0
            flaws = []
            
            for img in images:
                alt = img.get("alt")
                if alt is None:
                    images_without_alt += 1
                elif str(alt).strip() == "":
                    images_with_empty_alt += 1
            
            images_with_issues = images_without_alt + images_with_empty_alt
            
            # Calculate score
            if total_images == 0:
                score = 5  # No images, perfect score
            else:
                good_ratio = (total_images - images_with_issues) / total_images
                if good_ratio >= 0.95:
                    score = 5
                elif good_ratio >= 0.8:
                    score = 4
                elif good_ratio >= 0.6:
                    score = 3
                elif good_ratio >= 0.4:
                    score = 2
                elif good_ratio >= 0.2:
                    score = 1
                else:
                    score = 0
            
            if images_without_alt > 0:
                flaws.append(f"{images_without_alt} images missing alt attribute")
            if images_with_empty_alt > 0:
                flaws.append(f"{images_with_empty_alt} images have empty alt text")
            
            return {
                "score": score,
                "flaws": flaws,
                "total_images": total_images,
                "images_with_issues": images_with_issues,
                "images_without_alt": images_without_alt,
                "images_with_empty_alt": images_with_empty_alt,
                "pages_checked": 1
            }
        except Exception as e:
            return {"score": 0, "flaws": [str(e)], "total_images": 0}
    
    def _build_seo_result(self, data: Optional[Dict]) -> Optional[SEOAuditResult]:
        """Build SEO audit result"""
        if not data:
            return None
        return SEOAuditResult(
            score=data.get("score", 0),
            flaws=data.get("flaws", []),
            metadata=data.get("metadata")
        )
    
    def _build_ssl_result(self, data: Optional[Dict]) -> Optional[SSLAuditResult]:
        """Build SSL audit result"""
        if not data:
            return None
        return SSLAuditResult(
            score=data.get("score", 0),
            flaws=data.get("flaws", []),
            https_accessible=data.get("https_accessible", False),
            certificate_valid=data.get("certificate_valid", False),
            days_until_expiry=data.get("days_until_expiry"),
            hsts_enabled=data.get("hsts_enabled", False),
            redirects_to_https=data.get("redirects_to_https", False)
        )
    
    def _build_speed_result(self, data: Optional[Dict]) -> Optional[LoadSpeedAuditResult]:
        """Build load speed audit result"""
        if not data:
            return None
        return LoadSpeedAuditResult(
            score=data.get("score", 0),
            flaws=data.get("flaws", []),
            load_time_ms=data.get("load_time_ms"),
            dom_content_loaded_ms=data.get("dom_content_loaded_ms"),
            timing_details=data.get("timing_details")
        )
    
    def _build_responsiveness_result(self, data: Optional[Dict]) -> Optional[ResponsivenessAuditResult]:
        """Build responsiveness audit result"""
        if not data:
            return None
        return ResponsivenessAuditResult(
            score=data.get("score", 0),
            flaws=data.get("flaws", []),
            pages_checked=data.get("pages_checked", 0),
            viewport_meta_present=data.get("viewport_meta_present", False),
            mobile_friendly=data.get("mobile_friendly", False)
        )
    
    def _build_social_result(self, data: Optional[Dict]) -> Optional[SocialLinksAuditResult]:
        """Build social links audit result"""
        if not data:
            return None
        return SocialLinksAuditResult(
            score=data.get("score", 0),
            flaws=data.get("flaws", []),
            links_found=data.get("links_found", 0),
            links_accessible=data.get("links_accessible", 0),
            links_broken=data.get("links_broken", 0),
            social_platforms=data.get("social_platforms", [])
        )
    
    def _build_image_alt_result(self, data: Optional[Dict]) -> Optional[ImageAltAuditResult]:
        """Build image alt audit result"""
        if not data:
            return None
        return ImageAltAuditResult(
            score=data.get("score", 0),
            flaws=data.get("flaws", []),
            total_images=data.get("total_images", 0),
            images_with_issues=data.get("images_with_issues", 0),
            pages_checked=data.get("pages_checked", 0)
        )
    
    def _generate_summary(self, results: Dict, overall_score: float) -> str:
        """Generate a summary of the audit"""
        if overall_score >= 4:
            grade = "Excellent"
        elif overall_score >= 3:
            grade = "Good"
        elif overall_score >= 2:
            grade = "Fair"
        else:
            grade = "Poor"
        
        summary = f"Overall website health: {grade} ({overall_score:.1f}/5). "
        
        # Find weakest areas
        weak_areas = []
        for key, data in results.items():
            if isinstance(data, dict) and data.get("score", 5) < 3:
                weak_areas.append(key.replace("_", " ").title())
        
        if weak_areas:
            summary += f"Areas needing attention: {', '.join(weak_areas)}."
        else:
            summary += "All areas performing well."
        
        return summary
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # SEO recommendations
        seo = results.get('seo', {})
        if isinstance(seo, dict) and seo.get('score', 5) < 4:
            recommendations.append("Improve SEO by adding missing meta tags and Open Graph data")
        
        # SSL recommendations
        ssl = results.get('ssl', {})
        if isinstance(ssl, dict):
            if not ssl.get('certificate_valid', True):
                recommendations.append("Fix SSL certificate issues immediately")
            if not ssl.get('redirects_to_https', True):
                recommendations.append("Enable HTTP to HTTPS redirect")
            if not ssl.get('hsts_enabled', True):
                recommendations.append("Enable HSTS for better security")
        
        # Speed recommendations
        speed = results.get('speed', {})
        if isinstance(speed, dict) and speed.get('score', 5) < 4:
            recommendations.append("Optimize page load speed - consider image compression and caching")
        
        # Responsiveness recommendations
        resp = results.get('responsiveness', {})
        if isinstance(resp, dict) and not resp.get('mobile_friendly', True):
            recommendations.append("Improve mobile responsiveness - a significant portion of traffic is mobile")
        
        # Social links recommendations
        social = results.get('social', {})
        if isinstance(social, dict) and social.get('score', 5) < 3:
            recommendations.append("Add social media links to improve trust and engagement")
        
        # Image alt recommendations
        img = results.get('image_alt', {})
        if isinstance(img, dict) and img.get('score', 5) < 4:
            recommendations.append("Add descriptive alt text to images for SEO and accessibility")
        
        return recommendations
