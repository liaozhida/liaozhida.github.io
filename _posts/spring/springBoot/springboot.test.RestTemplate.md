# springboot.test.RestTemplate.md



##### Example 0
```
@Test
public void testA() throws Exception {

	MultiValueMap<String, Object> parts = new LinkedMultiValueMap<String, Object>();
	parts.add("amount", "777");
	parts.add("userId", userId);
	parts.add("mobile", "13728728332");
	parts.add("status", 0);
	parts.add("belong", 1);

	ResponseEntity<Message> entity = restTemplate.postForEntity("/ticket/tyj/gift", parts, Message.class);
	assertEquals(HttpStatus.OK, entity.getStatusCode());
	assertThat(entity.getBody().toString(), containsString("code=0"));
}

```

##### Example 1
```
@Test
public void loginRedirectsToGithub() throws Exception {
	TestRestTemplate restTemplate = new TestRestTemplate();
	ResponseEntity<Void> entity = restTemplate
			.getForEntity("http://localhost:" + this.port + "/login", Void.class);
	assertThat(entity.getStatusCode(), is(HttpStatus.FOUND));
	assertThat(entity.getHeaders().getLocation().toString(),
			startsWith("https://github.com/login/oauth"));
}

```

##### Example 2
```
@Test
public void everythingIsSecuredByDefault() throws Exception {
	TestRestTemplate restTemplate = new TestRestTemplate();
	ResponseEntity<Void> entity = restTemplate
			.getForEntity("http://localhost:" + this.port, Void.class);
	assertThat(entity.getStatusCode(), is(HttpStatus.FOUND));
	assertThat(entity.getHeaders().getLocation(),
			is(equalTo(URI.create("http://localhost:" + this.port + "/login"))));
}
```

##### Example 3
```
@Test
public void testHome() throws Exception {
	SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
			new SSLContextBuilder().loadTrustMaterial(null,
					new TrustSelfSignedStrategy()).build());

	HttpClient httpClient = HttpClients.custom().setSSLSocketFactory(socketFactory)
			.build();

	TestRestTemplate testRestTemplate = new TestRestTemplate();
	((HttpComponentsClientHttpRequestFactory) testRestTemplate.getRequestFactory())
			.setHttpClient(httpClient);
	ResponseEntity<String> entity = testRestTemplate.getForEntity(
			"https://localhost:" + this.port, String.class);
	assertEquals(HttpStatus.OK, entity.getStatusCode());
	assertEquals("Hello, Secret Property: chupacabras", entity.getBody());
}
```

##### Example 4
```
@Test
public void testHome() throws Exception {
    SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
            new SSLContextBuilder().loadTrustMaterial(null,
                    new TrustSelfSignedStrategy()).build());

    HttpClient httpClient = HttpClients.custom().setSSLSocketFactory(socketFactory)
            .build();

    TestRestTemplate testRestTemplate = new TestRestTemplate();
    ((HttpComponentsClientHttpRequestFactory) testRestTemplate.getRequestFactory())
            .setHttpClient(httpClient);
    ResponseEntity<String> entity = testRestTemplate.getForEntity(
            "https://localhost:" + this.port, String.class);
    assertEquals(HttpStatus.OK, entity.getStatusCode());
    assertEquals("Hello, world", entity.getBody());
}
```

##### Example 5
```
@Test
public void testHome() throws Exception {
    SSLConnectionSocketFactory socketFactory = new SSLConnectionSocketFactory(
                    new SSLContextBuilder().loadTrustMaterial(null,
                                    new TrustSelfSignedStrategy()).build());

    HttpClient httpClient = HttpClients.custom().setSSLSocketFactory(socketFactory)
                    .build();

    TestRestTemplate testRestTemplate = new TestRestTemplate();
    ((HttpComponentsClientHttpRequestFactory) testRestTemplate.getRequestFactory())
                    .setHttpClient(httpClient);
    ResponseEntity<String> entity = testRestTemplate.getForEntity(
                    "https://localhost:" + this.port, String.class);
    assertEquals(HttpStatus.OK, entity.getStatusCode());
    assertEquals("Hello World", entity.getBody());
}

```

[Java Code Examples for org.springframework.boot.test.TestRestTemplate](http://www.programcreek.com/java-api-examples/index.php?api=org.springframework.boot.test.TestRestTemplate)