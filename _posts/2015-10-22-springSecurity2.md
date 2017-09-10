接着上一篇：SpringSecurity 源码剖析(1)–用户登录过程发生了什么[附UML图]

上面的文章讲过，默认的过滤器链有十个过滤器，其中一个是FilterSecurityInterceptor，这个过滤器检查页面权限和放行，也就是我们这章要讲的重点。先看spring中的配置文件：

```Markup
<beans:bean id ="filterSecurityInterceptor"
    class= "org.springframework.security.web.access.intercept.FilterSecurityInterceptor" >
    <!-- 如何登陆用户失效的话 重新登陆验证 -->
    <beans:property name ="authenticationManager" ref= "AuthenticationManager"/>
    <beans:property name ="accessDecisionManager" ref= "affirmativeBased"/>
    <beans:property name ="securityMetadataSource">
          <filter-security-metadata-source >
                <!-- 用户角色 -->
                <intercept-url pattern ="/*/admin/*.html"  access="ROLE_ADMIN"/>
                <intercept-url pattern ="/*/charge/*.html"  access="ROLE_CHARGE,ROLE_ADMIN"/>
                <intercept-url pattern ="/*/stu/*.html"  access="ROLE_STUDENT,ROLE_CHARGE,ROLE_ADMIN"/>
                <!-- 登陆类型 -->
                <intercept-url pattern ="/*.html" access="IS_AUTHENTICATED_ANONYMOUSLY"/>
          </filter-security-metadata-source >
    </beans:property >
</beans:bean >
```

再看一下UML示例图，我们的主线逻辑以UML图和spring配置文件为思路：

QQ截图20151015171752

1. FilterSecurityInterceptor的调用invoke方法，主要是调用它的父类AbstractSecurityInterceptor的beforeInvocation方法
```java
public void invoke(FilterInvocation fi) throws IOException, ServletException {
    if ((fi.getRequest() != null) && (fi.getRequest().getAttribute(FILTER_APPLIED) != null)
            && observeOncePerRequest) {
        // filter already applied to this request and user wants us to observe
        // once-per-request handling, so don't re-do security checking
        fi.getChain().doFilter(fi.getRequest(), fi.getResponse());
    } else {
        // first time this request being called, so perform security checking
        if (fi.getRequest() != null) {
            fi.getRequest().setAttribute(FILTER_APPLIED, Boolean.TRUE);
        }
        
        //调用父类的权限验证方法
        InterceptorStatusToken token = super.beforeInvocation(fi);
 
        try {
            fi.getChain().doFilter(fi.getRequest(), fi.getResponse());
        } finally {
            super.finallyInvocation(token);
        }
 
        super.afterInvocation(token, null);
    }
}
```

2.FilterSecurityInterceptor的父类AbstractSecurityInterceptor执行验证操作，逻辑是获取spring的配置信息和保存在SecurityContext的Authentication信息，通过accessDecisionManager类进行比对，如果验证不通过即抛出异常。
```java
protected InterceptorStatusToken beforeInvocation(Object object) {
    Assert.notNull(object, "Object was null");
    final boolean debug = logger.isDebugEnabled();
 
    if (!getSecureObjectClass().isAssignableFrom(object.getClass())) {
        throw new IllegalArgumentException("Security invocation attempted for object "
                + object.getClass().getName()
                + " but AbstractSecurityInterceptor only configured to support secure objects of type: "
                + getSecureObjectClass());
    }
    
    //从spring配置文件中读取权限信息
    Collection<ConfigAttribute> attributes = this.obtainSecurityMetadataSource().getAttributes(object);
 
    //读取权限信息错误抛出异常
    if (attributes == null || attributes.isEmpty()) {
        if (rejectPublicInvocations) {
            throw new IllegalArgumentException("Secure object invocation " + object +
                    " was denied as public invocations are not allowed via this interceptor. "
                            + "This indicates a configuration error because the "
                            + "rejectPublicInvocations property is set to 'true'");
        }
 
        if (debug) {
            logger.debug("Public object - authentication not attempted");
        }
 
        publishEvent(new PublicInvocationEvent(object));
 
        return null; // no further work post-invocation
    }
 
    if (debug) {
        logger.debug("Secure object: " + object + "; Attributes: " + attributes);
    }
 
    //security上下文环境没有Authentication对象
    if (SecurityContextHolder.getContext().getAuthentication() == null) {
        credentialsNotFound(messages.getMessage("AbstractSecurityInterceptor.authenticationNotFound",
                "An Authentication object was not found in the SecurityContext"), object, attributes);
    }
 
    Authentication authenticated = authenticateIfRequired();
 
    try {
        //开始进行权限验证  重点关注
        this.accessDecisionManager.decide(authenticated, object, attributes);
    }
    catch (AccessDeniedException accessDeniedException) {
        publishEvent(new AuthorizationFailureEvent(object, attributes, authenticated, accessDeniedException));
 
        throw accessDeniedException;
    }
 
    if (debug) {
        logger.debug("Authorization successful");
    }
 
    if (publishAuthorizationSuccess) {
        publishEvent(new AuthorizedEvent(object, attributes, authenticated));
    }
 
    // Attempt to run as a different user
    Authentication runAs = this.runAsManager.buildRunAs(authenticated, object, attributes);
 
    if (runAs == null) {
        if (debug) {
            logger.debug("RunAsManager did not change Authentication object");
        }
 
        //   不需要调用 post-invocation
        //返回拦截结果实体
        return new InterceptorStatusToken(SecurityContextHolder.getContext(), false, attributes, object);
    } else {
        if (debug) {
            logger.debug("Switching to RunAs Authentication: " + runAs);
        }
 
        SecurityContext origCtx = SecurityContextHolder.getContext();
        SecurityContextHolder.setContext(SecurityContextHolder.createEmptyContext());
        SecurityContextHolder.getContext().setAuthentication(runAs);
 
        // 需要调用 post-invocation
        return new InterceptorStatusToken(origCtx, true, attributes, object);
    }
}
```

3.AbstractSecurityInterceptor类的AuthenticateIfRequired方法作用是从securityContext中获取Authentication实体，里面保存了登陆用户的各种权限信息
```java
private Authentication authenticateIfRequired() {
	//从上下文环境中取出authentication
    Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
 
    //对authentication有效性进行验证
    if (authentication.isAuthenticated() && !alwaysReauthenticate) {
        if (logger.isDebugEnabled()) {
            logger.debug("Previously Authenticated: " + authentication);
        }
 
        return authentication;
    }
 
    //如果autentication无效，比如过期了或者设置了多地登陆， 重新登陆处理
    authentication = authenticationManager.authenticate(authentication);
 
    if (logger.isDebugEnabled()) {
        logger.debug("Successfully Authenticated: " + authentication);
    }
 
    //将新的Authentication设置到上下文中
    SecurityContextHolder.getContext().setAuthentication(authentication);
 
    return authentication;
}
```

4.AbstractAccessDecisionManager（这个是关键的类）的子类AffirmativeBased执行decide方法，这个方法是调用各个Voter进行权限比对，RoleVoter类会进行投票，是否允许页面返回，这个比对规则是可以自定义的，默认是只要有一个返回ACCESS_GRANTED就代表验证失败
```java
public void decide(Authentication authentication, Object object, Collection<ConfigAttribute> configAttributes)
        throws AccessDeniedException {
    int deny = 0;
 
    //遍历每个Voter,进行权限验证  voter的类在spring配置文件中配置
    for (AccessDecisionVoter voter : getDecisionVoters()) {
        //权限验证
        int result = voter.vote(authentication, object, configAttributes);
 
        if (logger.isDebugEnabled()) {
            logger.debug("Voter: " + voter + ", returned: " + result);
        }
 
        //voter 投票
        switch (result) {
        case AccessDecisionVoter.ACCESS_GRANTED:
            return;
 
        case AccessDecisionVoter.ACCESS_DENIED:
            deny++;
 
            break;
 
        default:
            break;
        }
    }
 
    if (deny > 0) {
        throw new AccessDeniedException(messages.getMessage("AbstractAccessDecisionManager.accessDenied",
                "Access is denied"));
    }
 
    // To get this far, every AccessDecisionVoter abstained
    checkAllowIfAllAbstainDecisions();
}
```

5.其中之一的Voter：RoleVoter类继承自AccessDecisionVoter，通过返回常量值来判断是否比对正确，主要是比对用户角色是否正确
```java
public int vote(Authentication authentication, Object object, Collection<ConfigAttribute> attributes) {
    int result = ACCESS_ABSTAIN;
    //从Authentication中获取权限信息
    Collection<? extends GrantedAuthority> authorities = extractAuthorities(authentication);
 
    //将用户的权限信息 和 配置文件中的 权限信息进行比对
    for (ConfigAttribute attribute : attributes) {
        if (this.supports(attribute)) {
            result = ACCESS_DENIED;
 
            for (GrantedAuthority authority : authorities) {
                if (attribute.getAttribute().equals(authority.getAuthority())) {
                    return ACCESS_GRANTED;
                }
            }
        }
    }
 
    return result;
}
 
Collection<? extends GrantedAuthority> extractAuthorities(Authentication authentication) {
     return authentication.getAuthorities();
 }
```

6.其中之一的Voter：AuthenticatedVoter类继承自AccessDecisionVoter，主要是对比登陆类型

```java
/*对这种类型的 权限拦截 进行验证
 *<intercept-url pattern ="/*.html"  access="IS_AUTHENTICATED_ANONYMOUSLY"/> 
 */
public int vote(Authentication authentication, Object object, Collection<ConfigAttribute> attributes) {
    int result = ACCESS_ABSTAIN;
 
    //对权限类型进行比对
    for (ConfigAttribute attribute : attributes) {
        if (this.supports(attribute)) {
            result = ACCESS_DENIED;
            
            if (IS_AUTHENTICATED_FULLY.equals(attribute.getAttribute())) {
                if (isFullyAuthenticated(authentication)) {
                    return ACCESS_GRANTED;
                }
            }
 
            if (IS_AUTHENTICATED_REMEMBERED.equals(attribute.getAttribute())) {
                if (authenticationTrustResolver.isRememberMe(authentication)
                    || isFullyAuthenticated(authentication)) {
                    return ACCESS_GRANTED;
                }
            }
 
            if (IS_AUTHENTICATED_ANONYMOUSLY.equals(attribute.getAttribute())) {
                if (authenticationTrustResolver.isAnonymous(authentication) || isFullyAuthenticated(authentication)
                    || authenticationTrustResolver.isRememberMe(authentication)) {
                    return ACCESS_GRANTED;
                }
            }
        }
    }
 
    return result;
}
```

转载请务必著名出处，并带上可跳转的链接
