cannot be resolved to a type.md 

导入项目 出现 eclipse cannot be resolved to a type 这个错误

具体的情况： 显示 ApplicationContext 出现 Error 

ApplicationContext 是 spring-context.jar 中的，我的pom.xml 正确配置，项目的 Maven Dependencies 也看到了这个包在依赖中

尝试了几种办法：
- clean
- maven update
- refresh  

还是不能解决问题


删除maven 本地仓库  spring-context 的文件夹 ，重新拉取就好了
