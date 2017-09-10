

<div class="content-wrap">
          <div id="content" class="content">
            

  <div id="posts" class="posts-expand">
    

  

  
  
  

  <article class="post post-type-normal" itemscope="" itemtype="http://schema.org/Article" style="opacity: 1; display: block; transform: translateY(0px);">
    <link itemprop="mainEntityOfPage" href="http://nkcoder.github.io/2016/04/10/liquibase-in-maven-and-gradle/">

    <span hidden="" itemprop="author" itemscope="" itemtype="http://schema.org/Person">
      <meta itemprop="name" content="nkcoder">
      <meta itemprop="description" content="">
      <meta itemprop="image" content="/images/coder.png">
    </span>

    <span hidden="" itemprop="publisher" itemscope="" itemtype="http://schema.org/Organization">
      <meta itemprop="name" content="Think And Code">
    </span>

    
      <header class="post-header">

        
        
          <h2 class="post-title" itemprop="name headline">[转载]使用LiquiBase管理数据库的迁移</h2>
        

        <div class="post-meta">
          <span class="post-time">
            
              <span class="post-meta-item-icon">
                <i class="fa fa-calendar-o"></i>
              </span>
              
                <span class="post-meta-item-text">发表于</span>
              
              <time title="创建于" itemprop="dateCreated datePublished" datetime="2016-04-10T16:06:32+08:00">
                2016-04-10
              </time>
            

            

            
          </span>

          
            <span class="post-category">
            
              <span class="post-meta-divider">|</span>
            
              <span class="post-meta-item-icon">
                <i class="fa fa-folder-o"></i>
              </span>
              
                <span class="post-meta-item-text">分类于</span>
              
              
                <span itemprop="about" itemscope="" itemtype="http://schema.org/Thing">
                  <a href="/categories/Backend/" itemprop="url" rel="index">
                    <span itemprop="name">Backend</span>
                  </a>
                </span>

                
                
              
            </span>
          

          
            
              <span class="post-comments-count">
                <span class="post-meta-divider">|</span>
                <span class="post-meta-item-icon">
                  <i class="fa fa-comment-o"></i>
                </span>
                <a href="/2016/04/10/liquibase-in-maven-and-gradle/#comments" itemprop="discussionUrl">
                  <span class="post-comments-count disqus-comment-count" data-disqus-identifier="2016/04/10/liquibase-in-maven-and-gradle/" itemprop="commentCount">0 Comments</span>
                </a>
              </span>
            
          

          
          

          

          

          

        </div>
      </header>
    

    <div class="post-body" itemprop="articleBody">

      
      

      
        <blockquote>
<p>本文链接为：<a href="http://nkcoder.github.io/2016/04/10/liquibase-in-maven-and-gradle/">http://nkcoder.github.io/2016/04/10/liquibase-in-maven-and-gradle/</a>  ，转载请注明出处，谢谢！</p>
</blockquote>
<p><a href="http://www.liquibase.org/index.html" target="_blank" rel="external">LiquiBase</a>是一个用于数据库重构和迁移的开源工具，通过日志文件的形式记录数据库的变更，然后执行日志文件中的修改，将数据库更新或回滚到一致的状态。LiquiBase的主要特点有：</p>
<ul>
<li>支持几乎所有主流的数据库，如MySQL, PostgreSQL, Oracle, Sql Server, DB2等；</li>
<li>支持多开发者的协作维护；</li>
<li>日志文件支持多种格式，如XML, YAML, JSON, SQL等；</li>
<li>支持多种运行方式，如命令行、Spring集成、Maven插件、Gradle插件等；</li>
</ul>
<a id="more"></a>
<p>本文首先简单介绍一下LiquiBase的changelog文件的常用标签配置，然后介绍在Maven和Gradle中集成并运行LiquiBase。</p>
<h2 id="1-changelog文件格式"><a href="#1-changelog文件格式" class="headerlink" title="1. changelog文件格式"></a>1. changelog文件格式</h2><p>changelog是LiquiBase用来记录数据库的变更，一般放在<code>CLASSPATH</code>下，然后配置到执行路径中。</p>
<p>changelog支持多种格式，主要有XML/JSON/YAML/SQL，其中XML/JSON/YAML除了具体格式语法不同，节点配置很类似，SQL格式中主要记录SQL语句，这里仅给出XML格式和SQL格式的示例，更多的格式示例请参考<a href="http://www.liquibase.org/documentation/databasechangelog.html" target="_blank" rel="external">文档</a></p>
<p>changelog.xml</p>
<pre><code>&lt;changeSet id="2" author="daniel" runOnChange="true"&gt;
    &lt;insert tableName="contest_info"&gt;
        &lt;column name="id"&gt;3&lt;/column&gt;
        &lt;column name="title"&gt;title 3&lt;/column&gt;
        &lt;column name="content"&gt;content 3&lt;/column&gt;
    &lt;/insert&gt;
&lt;/changeSet&gt;
</code></pre><p>changelog.sql</p>
<pre><code>--liquibase formatted sql
--changeset daniel:16040707
CREATE TABLE `role_authority_sum` (
  `row_id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `role_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '关联role的role_id',
  `authority_sum` int(11) unsigned NOT NULL DEFAULT '0' COMMENT 'perms的值的和',
  `data_type_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '关联data_type的id',
  PRIMARY KEY (`row_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='角色的权限值的和，如角色有RD权限，则和为2+8=10';
</code></pre><h2 id="2-常用的标签及命令"><a href="#2-常用的标签及命令" class="headerlink" title="2. 常用的标签及命令"></a>2. 常用的标签及命令</h2><h3 id="2-1-标签"><a href="#2-1-标签" class="headerlink" title="2.1 标签"></a>2.1 <changeset>标签</changeset></h3><p>一个<code>&lt;changeSet&gt;</code>标签对应一个变更集，由属性<code>id</code>、<code>name</code>，以及changelog的文件路径唯一标识。changelog在执行的时候并不是按照id的顺序，而是按照changeSet在changelog中出现的顺序。</p>
<p>LiquiBase在执行changelog时，会在数据库中插入两张表：<code>DATABASECHANGELOG</code>和<code>DATABASECHANGELOGLOCK</code>，分别记录changelog的执行日志和锁日志。</p>
<p>LiquiBase在执行changelog中的changeSet时，会首先查看<code>DATABASECHANGELOG</code>表，如果已经执行过，则会跳过（除非changeSet的<code>runAlways</code>属性为true，后面会介绍），如果没有执行过，则执行并记录changelog日志；</p>
<p>changelog中的一个changeSet对应一个事务，在changeSet执行完后commit，如果出现错误则rollback；</p>
<p><code>&lt;changeSet&gt;</code>标签的主要属性有：</p>
<ul>
<li>runAlways：即使已经执行过，仍然每次都执行；<strong>注意</strong>: 由于<code>DATABASECHANGELOG</code>表中还记录了changeSet的MD5校验值MD5SUM，如果changeSet的<code>id</code>和<code>name</code>没变，而内容变了，则由于MD5值变了，即使runAlways的值为True，执行也是失败的，会报错。这种情况应该使用<code>runOnChange</code>属性。</li>
</ul>
<pre><code>[ERROR] Failed to execute goal org.liquibase:liquibase-maven-plugin:3.4.2:update (default-cli) on project tx_test: Error setting up or running Liquibase: Validation Failed:
[ERROR] 1 change sets check sum
</code></pre><ul>
<li><p>runOnChange：第一次的时候执行以及当changeSet的内容发生变化时执行。不受MD5校验值的约束。</p>
</li>
<li><p>runInTransaction：是否作为一个事务执行，默认为true。设置为false时需要<strong>小心</strong>：如果执行过程中出错了则不会rollback，数据库很可能处于不一致的状态；</p>
</li>
</ul>
<p><code>&lt;changeSet&gt;</code>下有一个重要的子标签<code>&lt;rollback&gt;</code>，即定义回滚的SQL语句。对于<code>create table</code>, <code>rename column</code>和<code>add column</code>等，LiquiBase会自动生成对应的rollback语句，而对于<code>drop table</code>、<code>insert data</code>等则需要显示定义rollback语句。</p>
<h3 id="2-2-lt-include-gt-与-lt-includeAll-gt-标签"><a href="#2-2-lt-include-gt-与-lt-includeAll-gt-标签" class="headerlink" title="2.2 <include>与<includeAll>标签"></a>2.2 <code>&lt;include&gt;</code>与<code>&lt;includeAll&gt;</code>标签</h3><p>当changelog文件越来越多时，可以使用<code>&lt;include&gt;</code>将文件管理起来，如：</p>

<h3 id="2-3-diff命令"><a href="#2-3-diff命令" class="headerlink" title="2.3 diff命令"></a>2.3 diff命令</h3><p>diff命令用于比较数据库之间的异同。比如通过命令行执行：</p>
<pre><code>java -jar liquibase.jar --driver=com.mysql.jdbc.Driver \
    --classpath=./mysql-connector-java-5.1.29.jar \
    --url=jdbc:mysql://127.0.0.1:3306/test \
    --username=root --password=passwd \
    diff \
    --referenceUrl=jdbc:mysql://127.0.0.1:3306/authorization \
    --referenceUsername=root --referencePassword=passwd
</code></pre><h3 id="2-4-generateChangeLog"><a href="#2-4-generateChangeLog" class="headerlink" title="2.4 generateChangeLog"></a>2.4 generateChangeLog</h3><p>在已有的项目上使用LiquiBase，要生成当前数据库的changeset，可以采用两种方式，一种是使用数据库工具导出SQL数据，然后changelog文件以SQL格式记录即可；另一种方式就是用<code>generateChangeLog</code>命令，如：</p>
<pre><code>liquibase --driver=com.mysql.jdbc.Driver \
      --classpath=./mysql-connector-java-5.1.29.jar \
      --changeLogFile=liquibase/db.changelog.xml \
      --url="jdbc:mysql://127.0.0.1:3306/test" \
      --username=root \
      --password=yourpass \
      generateChangeLog
</code></pre><p>不过<code>generateChangeLog</code>不支持以下功能：存储过程、函数以及触发器；</p>
<h2 id="3-Maven集成LiquiBase"><a href="#3-Maven集成LiquiBase" class="headerlink" title="3. Maven集成LiquiBase"></a>3. Maven集成LiquiBase</h2><h3 id="3-1-liquibase-maven-plugin的配置"><a href="#3-1-liquibase-maven-plugin的配置" class="headerlink" title="3.1 liquibase-maven-plugin的配置"></a>3.1 <code>liquibase-maven-plugin</code>的配置</h3><p>Maven中集成LiquiBase，主要是配置<code>liquibase-maven-plugin</code>，首先给出一个示例：</p>
<pre><code>&lt;plugin&gt;
  &lt;groupId&gt;org.liquibase&lt;/groupId&gt;
  &lt;artifactId&gt;liquibase-maven-plugin&lt;/artifactId&gt;
  &lt;version&gt;3.4.2&lt;/version&gt;
  &lt;configuration&gt;
      &lt;changeLogFile&gt;src/main/resources/liquibase/test_changelog.xml&lt;/changeLogFile&gt;
      &lt;driver&gt;com.mysql.jdbc.Driver&lt;/driver&gt;
      &lt;url&gt;jdbc:mysql://127.0.0.1:3306/test&lt;/url&gt;
      &lt;username&gt;root&lt;/username&gt;
      &lt;password&gt;passwd&lt;/password&gt;
  &lt;/configuration&gt;
  &lt;executions&gt;
      &lt;execution&gt;
          &lt;phase&gt;process-resources&lt;/phase&gt;
          &lt;goals&gt;
              &lt;goal&gt;update&lt;/goal&gt;
          &lt;/goals&gt;
      &lt;/execution&gt;
  &lt;/executions&gt;
&lt;/plugin&gt;
</code></pre><p>其中<code>&lt;configuration&gt;</code>节点中的配置可以放在单独的配置文件里。</p>
<p>如果需要在父项目中配置子项目共享的LiquiBase配置，而各个子项目可以定义自己的配置，并覆盖父项目中的配置，则只需要在父项目的pom中将<code>propertyFileWillOverride</code>设置为true即可，如：</p>
<pre><code>&lt;plugin&gt;
    &lt;groupId&gt;org.liquibase&lt;/groupId&gt;
    &lt;artifactId&gt;liquibase-maven-plugin&lt;/artifactId&gt;
    &lt;version&gt;3.4.2&lt;/version&gt;
    &lt;configuration&gt;
        &lt;propertyFileWillOverride&gt;true&lt;/propertyFileWillOverride&gt;
        &lt;propertyFile&gt;liquibase/liquibase.properties&lt;/propertyFile&gt;
    &lt;/configuration&gt;
&lt;/plugin&gt;
</code></pre><h3 id="3-2-liquibase-update"><a href="#3-2-liquibase-update" class="headerlink" title="3.2 liquibase:update"></a>3.2 <code>liquibase:update</code></h3><p>执行changelog中的变更：</p>
<pre><code>$ mvn liquibase:update
</code></pre><h3 id="3-3-liquibase-rollback"><a href="#3-3-liquibase-rollback" class="headerlink" title="3.3 liquibase:rollback"></a>3.3 <code>liquibase:rollback</code></h3><p>rollback有3中形式，分别是：</p>
<pre><code>- rollbackCount: 表示rollback的changeset的个数；
- rollbackDate：表示rollback到指定的日期；
- rollbackTag：表示rollback到指定的tag，需要使用LiquiBase在具体的时间点打上tag；
</code></pre><p><code>rollbackCount</code>比较简单，示例如：</p>
<pre><code>$ mvn liquibase:rollback -Dliquibase.rollbackCount=3
</code></pre><p><code>rollbackDate</code>需要注意日期的格式，必须匹配当前平台上执行<code>DateFormat.getDateInstance()</code>得到的格式，比如我的格式为<code>MMM d, yyyy</code>，示例如：</p>
<pre><code>$ mvn liquibase:rollback -Dliquibase.rollbackDate="Apr 10, 2016"
</code></pre><p><code>rollbackTag</code>使用tag标识，所以需要先打tag，示例如：</p>
<pre><code>$ mvn liquibase:tag -Dliquibase.tag=tag20160410
</code></pre><p>然后rollback到tag20160410，如：</p>
<pre><code>$ mvn liquibase:rollback -Dliquibase.rollbackTag=tag20160410
</code></pre><h2 id="4-Gradle集成LiquiBase"><a href="#4-Gradle集成LiquiBase" class="headerlink" title="4. Gradle集成LiquiBase"></a>4. Gradle集成LiquiBase</h2><p>首先在<code>build.gradle</code>中配置<code>liquibase-gradle-plugin</code>：</p>
<pre><code>buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath "org.liquibase:liquibase-gradle-plugin:1.2.1"
        classpath "mysql:mysql-connector-java:5.1.38"
    }
}
apply plugin: 'org.liquibase.gradle'
</code></pre><p>然后在<code>build.gradle</code>中配置该plugin的activities，其中一个activity表示一种运行环境：</p>
<pre><code>liquibase {
    activities {
        main {
            changeLogFile "src/main/resources/web-bundle-config/liquibase/main-changelog.xml"
            url "jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&amp;amp;characterEncoding=utf-8"
            username "root"
            password "yourpass"
        }
        test {
            main {
                changeLogFile "src/main/resources/web-bundle-config/liquibase/main-test-changelog.xml"
                url "jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&amp;amp;characterEncoding=utf-8"
                username "root"
                password "yourpass"
            }
        }
        runList = project.ext.runList
    }
}
</code></pre><p>比如执行main的命令为：</p>
<pre><code>$ gradle update -PrunList=main
</code></pre><h3 id="参考"><a href="#参考" class="headerlink" title="参考"></a>参考</h3><ol>
<li><a href="http://www.liquibase.org/documentation/index.html" target="_blank" rel="external">Building Changelogs</a></li>
<li><a href="http://stackoverflow.com/questions/11131978/how-to-tag-a-changeset-in-liquibase-to-rollback" target="_blank" rel="external">How to tag a changeset in liquibase to rollback</a></li>
<li><a href="http://izeye.blogspot.co.uk/2015/07/only-buildscript-and-other-plugins.html" target="_blank" rel="external">only buildscript {} and other plugins {} script blocks are allowed before plugins {} blocks, no other statements are allowed</a></li>
</ol>

      
    </div>

 




[官网-maven](http://www.liquibase.org/documentation/maven/maven_clearchecksums.html)
[官网-tutor](http://www.liquibase.org/documentation/changeset.html)
[maven-checksum](https://stackoverflow.com/questions/9995747/liquibase-checksum-validation-error-without-any-changes)
[使用LiquiBase管理数据库的迁移](https://nkcoder.github.io/2016/04/10/liquibase-in-maven-and-gradle/)