编辑JIRA系统设置的 base Url:
编辑 Bitbucket的 webhooks  地址
查看 JIRA 的应用程序 - Jenkins Configuration


#### BitBucket

- 去到[BitBucket](http://192.168.2.172:7990/) 创建相应的仓库
- 配置项目的权限
- 配置 webhooks 的 URL,格式如下： `<Jenkins_url>/buildByToken/build?job=<Jira_jobname>&token=<token>`  <token>在下一步的时候生成




#### Jenkins

- 去到[Jenkins](http://192.168.2.168:8080/)创建一个 Job
- 配置Job信息
	- 源码管理：选择Git,输入仓库的`SSH`地址，输入私钥
	- 构建触发器: 选择触发远程构建，输入 token
	- 构建：选择Execute shell ,输入脚本： 比如 `echo hello wold`
- 回到 Job面板，点击立即构建，查看结果是否成功


#### JIRA

- 去到[JIRA](http://192.168.2.173:8080/) 创建一个问题
- 点击 问题的右面版 - 开发 - 创建分支； 跳到Bitbucket界面，按照提示进行操作，我的测试分支是 `MAYD-4-hello1`
- 开发人员本地执行 `repo1 git:(MAYD-4-hello1) echo 'test' > index.html && gaa && gcmsg 'MAYD-4-hello1  #comment  hello commit' && gp`
- 回到问题面板 ，可以看到问题下面添加了新的注释: *hello commit*
- 回到Jenkins任务面板， 可以看到自动触发了一个构建







[smart commit](https://confluence.atlassian.com/bitbucket/processing-jira-software-issues-with-smart-commit-messages-298979931.html)

