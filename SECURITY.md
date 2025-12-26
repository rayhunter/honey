# 🔒 Security Documentation

This document outlines all security measures implemented in the Movie Recommender application.

## Security Features Implemented

### ✅ 1. API Key Protection
- **No API key logging**: API keys are never displayed or logged
- **Environment variables**: All secrets stored in `.env` or Streamlit secrets
- **Status indicators**: Only show "configured" or "not found" status

### ✅ 2. XSS (Cross-Site Scripting) Protection
- **HTML sanitization**: All user inputs are sanitized before rendering
- **Entity escaping**: HTML entities are properly escaped
- **URL validation**: External links validated to prevent `javascript:` and `data:` URLs
- **Safe attributes**: Added `rel="noopener noreferrer"` to all external links

### ✅ 3. Input Validation
- **Length limits**: Maximum 200 characters per movie title
- **Character validation**: Only allows alphanumeric and common punctuation
- **Pattern blocking**: Blocks suspicious patterns like `<script>`, `onclick=`, etc.
- **Minimum requirements**: Enforces minimum number of movies per partner

### ✅ 4. Prompt Injection Protection
- **LLM input sanitization**: User inputs sanitized before sending to AI
- **Pattern detection**: Removes "ignore previous instructions" type attacks
- **Newline removal**: Prevents prompt breaking via newlines
- **Token limiting**: Prevents token flooding attacks

### ✅ 5. Dependency Security
- **Updated packages**: All dependencies updated to latest secure versions
  - `streamlit`: 1.41.1
  - `openai`: 1.59.5
  - `requests`: 2.32.3
  - `reportlab`: 4.2.5
  - `python-dotenv`: 1.0.1

### ✅ 6. Rate Limiting
- **Request limits**: 5 requests per 60 seconds per session
- **Automatic blocking**: 5-minute block when limit exceeded
- **Session-based**: Tracks requests per user session
- **User feedback**: Shows countdown timer when blocked

### ✅ 7. Authentication (Optional)
- **Password protection**: Optional password authentication
- **Session management**: Secure session state handling
- **Brute force protection**: 2-second delay on failed login
- **Logout functionality**: Secure logout with session clearing

**To enable authentication:**
```bash
# In .env file or Streamlit secrets
APP_PASSWORD=your_secure_password_here
```

### ✅ 8. Error Message Sanitization
- **Information hiding**: Technical details hidden from users
- **Path removal**: File paths redacted from error messages
- **Key redaction**: API keys and tokens removed from errors
- **User-friendly**: Generic error messages for end users
- **Debug mode**: Sanitized details shown only in debug mode

### ✅ 9. Network Security
- **SSL verification**: All HTTPS requests verify SSL certificates
- **Request timeouts**: 10-second timeout prevents hanging
- **Connection handling**: Proper error handling for network failures

### ✅ 10. HTTP Security Headers
Recommended headers to configure at reverse proxy/CDN level:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## Deployment Security Checklist

### Before Deploying:

- [ ] Set strong `APP_PASSWORD` in environment variables
- [ ] Set all API keys as environment variables (never commit to git)
- [ ] Enable HTTPS on your hosting platform
- [ ] Configure security headers at CDN/reverse proxy level
- [ ] Enable CORS restrictions if needed
- [ ] Review and adjust rate limits based on expected traffic
- [ ] Test authentication flow
- [ ] Verify error messages don't leak sensitive info

### Railway/Render Deployment:

1. **Set Environment Variables:**
   ```
   OPENAI_API_KEY=sk-...
   DEEPSEEK_API_KEY=sk-...
   TMDB_API_KEY=...
   APP_PASSWORD=your_secure_password  # Optional
   ```

2. **Configure Cloudflare (if using):**
   - Enable "Always Use HTTPS"
   - Set security headers in Transform Rules
   - Enable Bot Fight Mode
   - Configure rate limiting rules

3. **Monitor Usage:**
   - Set up billing alerts for API usage
   - Monitor rate limit blocks
   - Review authentication logs

## Security Best Practices

### For Users:
1. Use strong, unique passwords for authentication
2. Don't share your deployment URL publicly without authentication enabled
3. Monitor API usage and costs regularly
4. Rotate API keys periodically

### For Developers:
1. Never commit `.env` files or API keys to git
2. Keep dependencies updated regularly
3. Review security patches for all packages
4. Test security features before deploying
5. Use environment-specific configurations
6. Implement proper logging (without sensitive data)

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainer directly rather than opening a public issue.

## Security Audits

Last security review: December 2025
Next scheduled review: Quarterly

## Compliance Notes

- **GDPR**: No personal data is stored or processed
- **API Terms**: Complies with OpenAI, DeepSeek, and TMDB API terms
- **Rate Limiting**: Prevents abuse and excessive API costs
- **Authentication**: Optional password protection available

## Additional Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Streamlit Security Best Practices](https://docs.streamlit.io/knowledge-base/deploy/authentication)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Security Level**: Production-Ready ✅


