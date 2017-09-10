引入applicationContext.xml.md


```
/**
 * @author zhidaliao
 * 
 * 如果需要引入 application.xml  需要定义这个类
 */

@Configuration
@ImportResource(locations={"classpath:context/applicationContext-AppConfig.xml","classpath:context/applicationContext-MvcConfig.xml"})
public class ConfigClass {
	
}

```