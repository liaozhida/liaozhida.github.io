## 基于Lucene的solr服务配置和基本操作

### 系统环境

1. solr版本为：solr-4.10.2，可在官网下载一个压缩包，里面有需要用到的各种文件   
2. web容器:tomcat7 官方推荐jetty,压缩包自带了jetty,java -jar start.jar即可；为了方便学习测试，现在tomcat下运行
3. java版本 javau67 (要求u25或者以上)
4. 系统:windows8*64    / Linux使用的测试机是CentOs5.10*64 


### 概念介绍

1. Lucene:
    1. 概念：基于Java的全文索引/检索引擎,不是产品，而是一个开源的jar包，使用java进行全文索引的处理
    2. 原理：将数据源（比如多篇文章）排序顺序存储的同时，有另外一个排好序的关键词列表，用于存储关键词==>文章映射关系，利用这样的映射关系索引：[关键词==>出现关键词的文章编号，出现次数（甚至包括位置：起始偏移量，结束偏移量），出现频率]，检索过程就是把模糊查询变成多个可以利用索引的精确查询的逻辑组合的过程。从而大大提高了多关键词查询的效率，所以，全文检索问题归结到最后是一个排序问题。
    3. 索引创新：大部分的搜索（数据库）引擎都是用B树结构来维护索引，索引的更新会导致大量的IO操作，Lucene在实现中，对此稍微有所改进：不是维护一个索引文件，而是在扩展索引的时候不断创建新的索引文件，然后定期的把这些新的小索引文件合并到原先的大索引中（针对不同的更新策略，批次的大小可以调整），这样在不影响检索的效率的前提下，提高了索引的效率
    4. 关于Lucene的详细内容附录补充
2. solr概念
    1. 是Apache Lucene项目的开源企业搜索平台，他是一个独立的全文搜索服务器，无需编码即可达到插入搜索的功能
3. 为什么选择lucene而不是数据库
    1. 根据相关度进行排序，让最相关的头100条结果满足98%以上用户的需求
    2. 数据库索引不是为全文索引设计的，因此，使用like "%keyword%"时，数据库索引是不起作用的，相对于lucene的全文检索效率低   

### 基础入门

#### 部署solr.war 运行tomcat，出现页面，说明部署solr服务器成功


- 需要设置solr文件夹路径，如果Solr 主目录没有指定则默认设置为solr/，可以通过以下任意一种方式实现

	- 配置tomcat server.xml配置，修改以下内容，将SOLR_HOME替换成你自己的SOLR_HOME路径。
	<Context path="" docBase="${SOLR_HOME}" reloadable="true"  crossContext="true"></Context>  
    - 通过JNDI 将主目录的路径绑定到java:comp/env/solr/home 。
    - 通过修改web.xml 位置在：src/web-app/web/WEB-INF

    ```	
    <env-entry>
	    <env-entry-name>solr/home</env-entry-name>
	    <env-entry-value>solr/</env-entry-value>
	    <env-entry-type>java.lang.String</env-entry-type>
	</env-entry> 
	```

    - 可以通过修改catalina.bat的方法，在首行加上

    ```
    set JAVA_OPTS=%JAVA_OPTS% -Dsolr.solr.home=D:\apache-tomcat-7.0.55-windows-x64\apache-tomcat-7.0.55\webapps\solr
    ```

    - 修改

	```
    System.setProperty("solr.solr.home", "/home/shalinsmangar/work/oss/branch-1.3/example/solr");
	```

    - 对于Linux系统，Solr的文件夹放在/usr/share/tomcat/下面（不同的linux发行版本根据报错信息配置文件夹路径即可），在我的测试环境中不用像windows一样做其他额外的设置。
- Linux系统需要将solr文件设置用户权限 chown -R tomcat solr
- 启动容器：通过输入网址 可以查看到主页面

#### 数据插入的几种方式：数据插入都需要在schema.xml中定义才能
    
- 使用javaAPI或其他客户端

```
public class Student {
      @Field
      private String id ;
      @Field
      private String name;
      @Field 
      private List<String> features; 
   
      
      public String getId() {
             return id;
      }
      public void setId(String id) {
             this. id = id;
      }
      public String getName() {
             return name;
      }
      public void setName(String name) {
             this. name = name;
      }
      public List<String> getFeatures() {
             return features;
      }
      public void setFeatures(List<String> features) {
             this. features = features;
      }
}


public class AddDataA {
      static HttpSolrServer server = null;
      
      public static void main(String[] args) {
             try {
                  System. out.println( "---connect---");
                   connecto();
                  System. out.println( "---addData---");
                   addD();
                  System. out.println( "---addDocs---");
                   addDoc();
                  System. out.println( "---queryData---");
                   queryD();
                  System. out.println( "---insertBean---");
                   insertBean();
                  System. out.println( "---queryBean---");
                   queryBean();
                  
            } catch (Exception e) {
                  e.printStackTrace();
            }
            
      }
      
      /**
       * 连接 solr服务器
       */
      static void connecto(){
            String url = "http://localhost:8080/solr-4.10.2/";
             server = new HttpSolrServer(url);
             server.setMaxRetries(1);  
             server.setConnectionTimeout(15000);
             server.setParser( new XMLResponseParser());
             server.setSoTimeout(1000);  
             server.setDefaultMaxConnectionsPerHost(100); 
             server.setMaxTotalConnections(100); 
             server.setFollowRedirects( false);  
             server.setAllowCompression( true); 
      }
      
      /**
       * 增加数据
       * @throws IOException
       * @throws SolrServerException
       */
      public static void addD() throws SolrServerException, IOException{
             //server.deleteByQuery( "*:*" ); 清空索引
            SolrInputDocument doc1 = new SolrInputDocument();
            doc1.addField( "id", "myID", 1.0f );
            doc1.addField( "name", "hello world", 1.0f );
            doc1.addField( "price", 10 );
             server.add(doc1);
             server.commit();   //手动commit
      }
      
      public static void addDoc() throws SolrServerException, IOException{
            SolrInputDocument doc1 = new SolrInputDocument();
            doc1.addField( "id", "id1", 1.0f );
            doc1.addField( "name", "doc1", 1.0f );
            doc1.addField( "price", 10 );
            SolrInputDocument doc2 = new SolrInputDocument();
            doc2.addField( "id", "id2", 1.0f );
            doc2.addField( "name", "doc2", 1.0f );
            doc2.addField( "price", 20 );
            Collection<SolrInputDocument> docs = new ArrayList<SolrInputDocument>();
            docs.add( doc1 );
            docs.add( doc2 );
             server. add( docs );
             server. commit();
      }
      
      /**
       * 对上一步添加的数据进行查询
       * @throws SolrServerException
       */
      public static void queryD() throws SolrServerException{
            SolrQuery solrQuery = new SolrQuery();
            solrQuery.setQuery( "q=hello world");
            QueryResponse queryResponse = null;
            queryResponse = server.query(solrQuery);
            
            System. out.println( "name-->"+queryResponse.getResults().get(0).getFieldValue( "name"));
            System. out.println( "id-->"+queryResponse.getResults().get(0).getFieldValue( "id"));
            System. out.println( "price-->"+queryResponse.getResults().get(0).getFieldValue( "price"));
      }
      
      /**
       * 插入Bean
       * @throws SolrServerException
       * @throws IOException
       */
      public static void insertBean() throws IOException, SolrServerException{
            Student stu = new Student();
            stu.setId( "no1");
            stu.setName( "liaozhida");
            stu.setFeatures(Arrays. asList("1","2","3"));
             server.addBean(stu);
             server.commit();
      }
      
      /**
       * 查询插入的bean数据
       * @throws SolrServerException
       */
      public static void queryBean() throws SolrServerException{
            SolrQuery solrQuery = new SolrQuery();
            solrQuery.setQuery( "q=1");
             //solrQuery.setQuery("q=liaozhida");  //也是可以的
            QueryResponse queryResponse= server.query(solrQuery); 
            List<Student> items = queryResponse.getBeans(Student. class);
            System. out.println( "list-->"+items.get(0).getFeatures());
      }
      
}
```

	console输出：

	```
	---connect---
	---addData---
	---addDocs---
	---queryData---
	name-->hello world
	id-->myID
	price-->10.0
	---insertBean---
	---queryBean---
	list-->[1, 2, 3]
	```

- Data Import Handler (DIH)从数据库导入
    - 在数据库储存数据
    - 准备相关的包：mysql-connector-java-5.1.34
    - solrconfig.xml配置requestHandler
    
    ```	
    <requestHandler name="/dataimport" class="org.apache.solr.handler.dataimport.DataImportHandler">
	      <lst name="defaults">
	        <str name="config">db-data-config.xml</str>
	      </lst>
	</requestHandler>
	``` 

    ```
    <lib dir="D:\apache-tomcat-7.0.55-windows-x64\apache-tomcat-7.0.55\webapps\solr-4.10.2-dist\dist"  regex="solr-dataimporthandler-\d.*\.jar"/>
	<lib dir="D:\apache-tomcat-7.0.55-windows-x64\apache-tomcat-7.0.55\webapps\solr-4.10.2-dist\contrib\dataimporthandler-extras\lib\" regex=".*\.jar" />
	```

    - 在相同的文件夹下创建db-data-config.xml
    
    ```
    <dataConfig>
	     <dataSource driver="com.mysql.jdbc.Driver"  url="jdbc:mysql://localhost:3306/solr" user="root" password="admin"/>
	     <document>
	     <entity name="user" query="SELECT id,name from t_user">
	              <field column="id" name="id" />
	              <field column="name" name="name" />
	     </entity>
	     </document>
	</dataConfig> 
	```

    - http请求触发数据导入：http://localhost:8080/solr-4.10.2/dataimport?command=full-import       http://114.215.177.242:8080/solr-4.10.2/dataimport?command=full-import&commit=true&optimize=true
        - 全导入，删除旧有索引：command=full-import
        - 不删除旧索引：&clean=false
        - 批量导入（full-import）：
        - 增量导入（delta-import）：
            1. Solr 读取conf/dataimport.properties 文件，得到solr最后一次执行索引操作的时间戳last_index_time，以及单个实体最后一次执行索引的时间戳：entity_name.last_index_time
            2. Solr对指定的实体使用deltaImportQuery SQL查询得到insert或update时间戳大于${dataimporter.last_index_time}需要增量索引的字段，然后调用deltaQuery对符合条件需要执行增量索引的文档的字段进行索引，并更新dataimport.properties 的时间戳
        - 导入状态查询（status）：
        - 重新装载配置文件（reload-config）
        - 终止导入（abort）：
    - 第六步：验证我们的索引，打开浏览器，输入：http://localhost:8080/solr-4.10.2/select/?q=tom
        1. 
- 文件导入：JSON文档，用 Solr Cell (ExtractingRequestHandler)索引诸如Word和PDF之类的二进制文档，CSV文件,包括从Excel或MySQL导入的文件
    1. 通过网页界面可以引入，略
- 网页界面操作导入
    1. 插入
    2. 查询不能使用ID值作为查询条件
    3. 其他操作忽略

#### 对于中文的支持

1. 分词产品 目前Lucene 的中文分词主要有：
paoding ：Lucene 中文分词“庖丁解牛” Paoding Analysis 。
imdict ：imdict 智能词典所采用的智能中文分词程序。
mmseg4j ： 用 Chih-Hao Tsai 的 MMSeg 算法 实现的中文分词器。
ik ：采用了特有的“正向迭代最细粒度切分算法“，多子处理器分析模式。

2. 分词效率： 各个分词产品官方提供的性能数据：
paoding ：在PIII 1G 内存个人机器上，1 秒 可准确分词 100 万 汉字。
imdict ：483.64 ( 字节/ 秒) ，259517( 汉字/ 秒) 。
mmseg4j ： complex 1200kb/s 左右, simple 1900kb/s 左右。
ik ：具有 50 万字 / 秒的高速处理能力。

3. 自定义词库支持度
paoding ：支持不限制个数的用户自定义词库，纯文本格式，一行一词，使用后台线程检测词库的更新，自动编译更新过的词库到二进制版本，并加载
imdict ：暂时不支持用户自定义词库。但 原版 ICTCLAS 支持。支持用户自定义 stop words
mmseg4j ：自带 sogou 词库，支持名为 wordsxxx.dic ， utf8 文本格式的用户自定义词库，一行一词。不支持自动检测。 -Dmmseg.dic.path
ik ： 支持 api 级的用户词库加载，和配置级的词库文件指定，无 BOM 的 UTF-8 编码， \r\n 分割。不支持自动检测。
ik 与 solr 集成

4. 权衡：中文分词首选IK和MMseg4j ,mmseg4j综合性能略高,两者的综合对比参考博文：http://www.cnblogs.com/wgp13x/p/3748764.html

5. 自带的分词效果：全文分词会将每一个字字分拆
       
6. mmseg4j配置：

- 打开文件
- 所需要的jar包:mmseg4j-core-1.10.0/mmseg4j-solr-2.2.0，网上有说需要mmseg4j-analysis-1.9.1包的,但是mmseg4j-solr-2.2.0已经包括了修改版的mmseg4j-analysis.jar在内了，旧版的有个类有问题，为了避免冲突，请不要引入mmseg4j-analysis-1.9.1

- mmseg4j---schema.xml

```
<fieldType name="text_mmseg4j_complex" class="solr.TextField" positionIncrementGap="100" > 
    <analyzer> 
        <tokenizer class="com.chenlb.mmseg4j.solr.MMSegTokenizerFactory" mode="complex" dicPath="dic"/> 
    </analyzer> 
</fieldType> 
<fieldType name="text_mmseg4j_maxword" class="solr.TextField" positionIncrementGap="100" > 
    <analyzer> 
        <tokenizer class="com.chenlb.mmseg4j.solr.MMSegTokenizerFactory" mode="max-word" dicPath="dic"/> 
    </analyzer> 
</fieldType> 
<fieldType name="text_mmseg4j_simple" class="solr.TextField" positionIncrementGap="100" > 
    <analyzer> 
      <!--
        可以通过以下定义自己的词库
        <tokenizer class="com.chenlb.mmseg4j.solr.MMSegTokenizerFactory" mode="simple" dicPath="n:/OpenSource/apache-solr-1.3.0/example/solr/my_dic"/>
        -->
        <tokenizer class="com.chenlb.mmseg4j.solr.MMSegTokenizerFactory" mode="simple" dicPath="dic"/>    
    </analyzer> 
</fieldType>
```
- 添加分词名

```
<field name="mmseg4j_complex_name" type="text_mmseg4j_complex" indexed="true" stored="true"/>
<field name="mmseg4j_maxword_name" type="text_mmseg4j_maxword" indexed="true" stored="true"/>
<field name="mmseg4j_simple_name" type="text_mmseg4j_simple" indexed="true" stored="true"/>
```
- 重启tomcat进行测试 
        - mmseg4j几种分词模式
            - mmseg4j_complex_name：根据词库复杂匹配，切分之后效果最好，切分耗时高，全文搜索耗时最低
            - mmseg4j_maxword_name：最零碎的切分，切分之后词量最多，切分耗时低，搜索耗时高，单个切分词不超过两个
            - mmseg4j_simple_name：根据词库简单匹配,切分之后效果略差，切分耗时低，搜索耗时低
        - 自定义词库:“格隆汇”是一个公司名，上图可见都被拆分了，尝试添加词库可以解决这个问题
            - mmseg4j-core.jar自带词库，在data路径下，分别是units/words/chars.dic ，分别是单位/词语/单个字的匹配规则
            - 自定义词库文件必须words 开头和 .dic结尾 而且文件编码是 必须是utf-8
            - 可以新建一个文件夹放分词文件，然后在schemal.xml中配置，也可以在mmseg4j-core.jar中添加，我把新词库放在mmseg4j-core.jar中，成功
             
#### 实际案例：

一个网站内搜索股票名称，股票代码号，相关帖子文章，要求能后台控制搜索的排名，比如名字优先/行业优先，思路如下

- 自定义词库，将行业相关的词语写入词库
- 将user_table/post_table/stock_code_table 数据导入solr进行索引生成
- 对于数据的增删改查使用触发器，每次操作发起请求http://host:8080/solor/update_XX,Mysql使用组件mysql-udf-http
- 排名权重(自定义结果排序)：
    1. 通过设置查询的qf,df,pf自定义权重，通过修改id权重为1得到下图结果




#### 将过程中遇到的问题列出来，方便大家解决

1. Unsupported major.minor version 51.0 (unable to load class org.apache.solr.servlet.SolrDispatch Filter) 
    1. 最新的Lucene只支持java7u25的版本
    2. 虽然环境已经是u25的版本，但还是出现这个问题，修改tomcat的jre启动版本，问题解决 
2. java.lang.NoClassDefFoundError: Failed to initialize Apache Solr: Could not find necessary SLF4j logging jars. If using Jetty, the SLF4j logging jars need to go in the jetty lib/ex
t directory. For other containers, the corresponding directory should be used. For more information, see: http://wiki.apache.org/solr/SolrLogging
    1. 因为我们使用的是tomcat容器，为了解决这个问题，直接去官网提供的网址看看怎么回事，在官网的介绍中看到这么一个段落：To get the same logging setup in another container (Tomcat for example) as with the example Jetty server, you need to do the following：Copy the jars from solr/example/lib/ext into your container's main lib directory. These jars will set up SLF4J and log4j.  将solr/example/lib/ext里的包复制到webapp中
    2. 缺失什么包就加入什么包
    3. 将solr-4.10.2-dist\example\resources\log4j.properties复制到webapp下的classpath
    4. 启动tomcat即可
3. Unsupported major.minor version 51.0
    1. 还是一样 调整IDE 的 jdk编译版本




删除：http://114.215.177.242:8080/solr-4.10.2/update/?stream.body=<delete><query>*:*</query></delete>&stream.contentType=text/xml;charset=utf-8&commit=true

df - 默认的查询字段，一般默认指定。

fq 值是一个查询，用于过滤查询结果，在负责查询时，可以很好的提高查询效率，fq 查询的内容会被缓存着，下次使用相同的过滤查询时，可以从缓存中命中。使用 fq 参数时需要注意以下几点：
* 在一个查询中，fq 参数可以设置多次。结果中将返回这些过滤条件的交集。例子中将返回 popularity 值大于10 ，并且 section 为 0 的文档
fq=popularity:\[10 TO *\] & fq=section:0


1. ModifiableSolrParams params = new ModifiableSolrParams();  
2. SolrQuery filterQuery = new SolrQuery();  
3. filterQuery.addFilterQuery("a:[1 TO *]");  
4. filterQuery.addFilterQuery("b:[2 TO *]");  
5. params.add(filterQuery);  

1. q=*:*&fq=a:[1 TO *]&fq=b:[2 TO *]  

即a大于等于1并且b大于等于


fq字段的类型尽量String   必须是index=true的


生效：！
如果使用
ModifiableSolrParams params = new ModifiableSolrParams();
params.set("fq", "a:[1 TO *]");
params.set("fq", "b:[2 TO *]");

那么a的条件会被覆盖，只有b的条件才生效。

正确的做法为：
ModifiableSolrParams params = new ModifiableSolrParams();
SolrQuery filterQuery = new SolrQuery();
filterQuery.addFilterQuery("a:[1 TO *]");
filterQuery.addFilterQuery("b:[2 TO *]");
params.add(filterQuery);

参考:http://my.oschina.net/junfrank/blog/286417?p=1


《filed stored 字段为true才会被储存 

<filed   type="string"   type="text_general"
type="string"    不能高亮显示  也不能个别字索引成功  必须全匹配
 type="text_general"   可以高亮显示   也可以全文索引

https://cwiki.apache.org/confluence/display/solr/Filter+Descriptions#FilterDescriptions-NGramFilter

英文分词等：
<fieldType name="text_general" class="solr.TextField" positionIncrementGap="100">
  <analyzer type="index">
    <tokenizer class="solr.StandardTokenizerFactory"/>
     <filter class="solr.EdgeNGramFilterFactory" minGramSize="1" maxGramSize="5"/>
    <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt" />
    <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="1" catenateNumbers="1" catenateAll="0"/>
    <!-- in this example, we will only use synonyms at query time
    <filter class="solr.SynonymFilterFactory" synonyms="index_synonyms.txt" ignoreCase="true" expand="false"/>
    -->
    <filter class="solr.LowerCaseFilterFactory"/>
  </analyzer>
  <analyzer type="query">
    <tokenizer class="solr.StandardTokenizerFactory"/>
    <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt" />
    <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
    <filter class="solr.LowerCaseFilterFactory"/>
    <filter class="solr.EdgeNGramFilterFactory" minGramSize="1" maxGramSize="5"/>
    <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="0" catenateNumbers="0" catenateAll="0"/>
  </analyzer>
</fieldType>


这里测试

注意！索引需要重建才会生效


Setting "df" (default field) from solrj?

solrQuery.add("df", "SearchText") 

某个字段不能被索引：在schema中添加   <copyField source="username" dest="text"/>     记得百度一下

主要参考文档(致谢)：
1. solr/doc/tutorial.html
2. http://outofmemory.cn/code-snippet/3588/Apache-Solr-chuji-course-introduction-install-bushu-Java-interface-zhongwen-fenci
3. http://www.ibm.com/developerworks/cn/java/j-solr-lucene/
4. http://blog.csdn.net/jaynol/article/details/24776437
5. http://tech.meituan.com/solr-spatial-search.html
6. http://blog.csdn.net/zhangchi_/article/details/9039801 //自定义排序
7. http://www.lifeba.org/arch/solr_functionquery.html   //自定义排序


