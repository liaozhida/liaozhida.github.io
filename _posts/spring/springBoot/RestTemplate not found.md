RestTemplate not found.md


添加下面的代码
```
@Bean
public RestTemplate restTemplate() {
	return new RestTemplate();
}
```