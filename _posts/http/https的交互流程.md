https的交互流程.md

There is no way to redirect invalid SSL. Redirecting from HTTPS to HTTP first needs a successful SSL connection so that the redirect can be done at the HTTP level inside the SSL connection. Failing to establish the SSL connection in the first place (because invalid) thus makes it impossible to get to the redirect at the HTTP level.