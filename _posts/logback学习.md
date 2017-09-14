### 1
基本选择规则依赖于被调用的 logger 的有效级别,而不是 appender 所关联的 logger 的级别。Logback 首先判断记录语句是否被启用,如果启用,则调用 logger 等级里的 appender, 无视 logger 的级别。配置文件 sample4.xml 演示了这一点。
```
<logger name="chapters.configuration" level="INFO" />
<root level="OFF">
	<appender-ref ref="STDOUT" />
</root>
```