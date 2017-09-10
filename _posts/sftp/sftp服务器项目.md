# sftp服务器项目

```
mkdir -p /mnt/doc/fengjr/inst-sftp/upload
mkdir -p /mnt/doc/fengjr/inst-sftp/download
mkdir -p /mnt/doc/tester/inst-sftp/upload
mkdir -p /mnt/doc/tester/inst-sftp/download

chmod 775 inst-sftp

apt-get install openssh-server
```

创建 SFTP 用户，并配置相应权限：

```
sudo adduser fengjr-admin
sudo addgroup fengjr
sudo usermod -G fengjr fengjr-admin  -s /bin/false   
//指定的shell脚本 不能ssh登录和操作命令


sudo adduser zhida   
sudo addgroup tester
sudo usermod -G tester zhida -s /bin/false


//liaozhida  passwd

```

创建 SSH 用户组，并把管理员加入到该组（注意 usermod 中的 -a 参数的意思是不从其他用户组用移除）

```
sudo addgroup ssh-users
sudo usermod -a -G ssh-users root
```

修改权限

```
cd /mnt/doc/tester/inst-sftp
chgrp -R tester inst-sftp
chmod -R 775 inst-sftp

cd /mnt/doc/fengjr/inst-sftp
chgrp -R fengjr inst-sftp
chmod -R 775 inst-sftp

```

修改配置文件

```
vim /etc/ssh/sshd_config
# 在 sshd_config 文件的最后，添加以下内容：

AllowGroups ssh-users fengjr tester

Match Group fengjr
    ChrootDirectory /mnt/doc/fengjr		
    AllowTcpForwarding no
    X11Forwarding no
    ForceCommand internal-sftp					

Match Group tester
    ChrootDirectory /mnt/doc/tester		 
    AllowTcpForwarding no
    X11Forwarding no
    ForceCommand internal-sftp	


//只能在当前目录
// 只能使用sftp命令
```

```
reboot
```

测试
```
sftp fengjr-XX@112.74.22.XX
sftp zhida@112.74.22.65
```

修改文件归属和权限

```
String group = "GROUP_NAME";
UserPrincipalLookupService lookupService = FileSystems.getDefault()
            .getUserPrincipalLookupService();
GroupPrincipal group = lookupService.lookupPrincipalByGroupName(group);
Files.getFileAttributeView(p, PosixFileAttributeView.class,
            LinkOption.NOFOLLOW_LINKS).setGroup(group);

File originalFile = new File("original.jpg"); // just as an example
GroupPrincipal group = Files.readAttributes(originalFile.toPath(), PosixFileAttributes.class, LinkOption.NOFOLLOW_LINKS).group();
Set the group owner of a file

File targetFile = new File("target.jpg");
Files.getFileAttributeView(targetFile.toPath(), PosixFileAttributeView.class, LinkOption.NOFOLLOW_LINKS).setGroup(group);


    
Prior to Java 6, there is no support of file permission update at Java level. You have to implement your own native method or call Runtime.exec() to execute OS level command such as chmod.

Starting from Java 6, you can useFile.setReadable()/File.setWritable()/File.setExecutable() to set file permissions. But it doesn't simulate the POSIX file system which allows to set permission for different users. File.setXXX() only allows to set permission for owner and everyone else.

Starting from Java 7, POSIX file permission is introduced. You can set file permissions like what you have done on *nix systems. The syntax is :

File file = new File("file4.txt");
file.createNewFile();

Set<PosixFilePermission> perms = new HashSet<>();
perms.add(PosixFilePermission.OWNER_READ);
perms.add(PosixFilePermission.OWNER_WRITE);

Files.setPosixFilePermissions(file.toPath(), perms);

```


```
FROM docker.umiit.cn:5043/maven:3.3.9


ADD ifex*.jar /usr/local/maven/ifex.jar

ADD classes/keyStore.properties /usr/local/maven/keyStore.properties
ADD classes/email.properties /usr/local/maven/email.properties

CMD ["adduser --quiet --disabled-password --shell /bin/false --home /home/fengjr-admin --gecos "User" fengjr-admin"]
CMD ["echo "fengjr-admin:fengjr-admin!@#" | chpasswd"]
CMD ["sudo addgroup fengjr"]
CMD ["sudo usermod -G fengjr fengjr-admin  -s /bin/false"]

CMD ["java", "-jar","ifex.jar","keyStore.properties","email.properties"]

```

```

down vote
accepted
The trick is to use useradd instead of its interactive wrapper adduser. I usually create users with:

RUN useradd -ms /bin/bash newuser
which creates a home directory for the user and ensures that bash is the default shell.

You can then add:

USER newuser
WORKDIR /home/newuser
to your dockerfile. Every command afterwards as well as interactive sessions will be executed as user newuser:

docker run -t -i image
newuser@131b7ad86360:~$



or 

RUN adduser --disabled-password --gecos '' newuser


or

# quietly add a user without password
adduser --quiet --disabled-password --shell /bin/bash --home /home/newuser --gecos "User" newuser

# set password
echo "newuser:newpassword" | chpasswd

```


### 注意要点

- ChrootDirectory设置的目录权限及其所有的上级文件夹权限，属主和属组必须是root；
- ChrootDirectory设置的目录权限及其所有的上级文件夹权限，只有属主能拥有写权限，也就是说权限最大设置只能是755。
- 所以要设置权限只能是创建子目录，然后重新赋权限 ,需要注意： 赋权的时候加上参数 `-R` 遍历每个子目录 

## jsch 连接服务器的坑

#### session timeout conect

会话设置的超时时间过短，参数值是毫秒，过短导致抛出异常

#### session.connect hang up

调用session.connect()方法没有响应，挂起等待。但是连接以前购买的阿里云服务器ServerA 却没有问题，几个方面

- 阿里云的安全组设置了IP权限：将程序部署在同一个机器上，依然存在相同的问题.
- 代码编写错误: 代码能连接ServerA ，但是不能连接ServerB 。
- 服务器sftp设置错误：将ServerA的所有配置都重新配置在初始化的ServerB 上面，依然出问题
- jar包版本不一致的问题：将版本升级大鹏 jsch 0.1.52 ，重新调用方法，不再挂起，抛出其他异常，解决挂起的问题


#### com.jcraft.jsch.JSchException: Algorithm negotiation fail

存在几种可能性

- sftp服务器的加密方式不支持，需要额外配置
[参考网站](http://stackoverflow.com/questions/30846076/jsch-algorithm-negotiation-fail)

- Java1.7 的安全机制不支持 
JSch doesn't do hmac-md5 and aes256-cbc is disabled because of your Java policy files. Two things you could try are...
[oracle jce 下载链接](http://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html) 下载文件 替换jre/lib/security的两个jar包(最好删除了再迁移)

#### java.io.IOException - End of IO Stream Read

jsch不兼容 OpenSSH最新版本
There was an interoperability problem with older versions of Jsch (e.g. 0.1.52) and recent versions of openssh (e.g OpenSSH_7.2p2). The problem went away for me after upgrading to Jsch 0.1.54.

```
Writer writer = new BufferedWriter(new OutputStreamWriter(
		              new FileOutputStream(path + File.separator + fileName,true), "utf-8"));
			writer.write(content);
			writer.close();
```

```
MessageFormat.format((String) props.get("WelcomeMessage"), "First", "Last");
Note that your properties files should have index of parameters instead of named parameters as below.

WelcomeMessage=Welcome Mr. {0} {1} !!!
```

```
package com.mkyong.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Controller
public class UploadController {

    //Save the uploaded file to this folder
    private static String UPLOADED_FOLDER = "F://temp//";

    @GetMapping("/")
    public String index() {
        return "upload";
    }

    @PostMapping("/upload") // //new annotation since 4.3
    public String singleFileUpload(@RequestParam("file") MultipartFile file,
                                   RedirectAttributes redirectAttributes) {

        if (file.isEmpty()) {
            redirectAttributes.addFlashAttribute("message", "Please select a file to upload");
            return "redirect:uploadStatus";
        }

        try {

            // Get the file and save it somewhere
            byte[] bytes = file.getBytes();
            Path path = Paths.get(UPLOADED_FOLDER + file.getOriginalFilename());
            Files.write(path, bytes);

            redirectAttributes.addFlashAttribute("message",
                    "You successfully uploaded '" + file.getOriginalFilename() + "'");

        } catch (IOException e) {
            e.printStackTrace();
        }

        return "redirect:/uploadStatus";
    }

    @GetMapping("/uploadStatus")
    public String uploadStatus() {
        return "uploadStatus";
    }

}

<form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file" /><br/><br/>
    <input type="submit" value="Submit" />
</form>
```

```
@RequestMapping(value = "/files/{fileID}", method = RequestMethod.GET)
    public void getFile(
        @PathVariable("fileID") String fileName, 
        HttpServletResponse response) throws IOException {
            String src= DestLocation.concat("\\"+fileName+".jar");
            InputStream is = new FileInputStream(src);
            IOUtils.copy(is, response.getOutputStream());
            response.flushBuffer();
    }
```

字段间的分隔符是其它字符或字符串，最常见的是逗号或制表符

Comma-Separated Values，CSV
Tab-Separated Values, TSV

进入FTP服务器  获取文件信息
```
public static String oldestFile() {
    Vector list = null;
    int currentOldestTime;
    int nextTime = 2140000000; //Made very big for future-proofing
    ChannelSftp.LsEntry lsEntry = null;
    SftpATTRS attrs = null;
    String nextName = null;
    try {
        list = Main.chanSftp.ls("*.xml");
        if (list.isEmpty()) {
            fileFound = false;
        }
        else {
            lsEntry = (ChannelSftp.LsEntry) list.firstElement();
            oldestFile = lsEntry.getFilename();
            attrs = lsEntry.getAttrs();
            currentOldestTime = attrs.getMTime();
            for (Object sftpFile : list) {
                lsEntry = (ChannelSftp.LsEntry) sftpFile;
                nextName = lsEntry.getFilename();
                attrs = lsEntry.getAttrs();
                nextTime = attrs.getMTime();
                if (nextTime < currentOldestTime) {
                    oldestFile = nextName;
                    currentOldestTime = nextTime;
                }
            }
            attrs = chanSftp.lstat(Main.oldestFile);
            long size1 = attrs.getSize();
            System.out.println("-Ensuring file is not being written to (waiting 1 minute)");
            Thread.sleep(60000); //Wait a minute to make sure the file size isn't changing
            attrs = chanSftp.lstat(Main.oldestFile);
            long size2 = attrs.getSize();
            if (size1 == size2) {
                System.out.println("-It isn't.");
                fileFound = true;
            }
            else {
                System.out.println("-It is.");
                fileFound = false;
            }
        }
    } catch (Exception ex) {ex.printStackTrace();}
    return Main.oldestFile;
}
```

    
 操作类型 | 创建时间   |  修改时间 | 访问时间 |
 ---------- | ---------- | ---------- | ---------- | 
 移动文件  |  不改变  |  不改变   |     改变
 复制文件  | 改变     | 不改变   |    改变
 修改文件  |  不改变  |   改变   | 改变

添加白名单

#### 接口

vi blockips.conf

```
allow 58.250.169.6;
allow 180.150.176.46;
allow 123.59.115.118;
deny all;
```

vi nginx.conf
```
include /etc/nginx/conf.d/blockips.conf;
```

vi docker-compose.yml 
```
nginx:
  restart: always
  image: jwilder/nginx-proxy:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - /root/docker/common/nginx_conf:/etc/nginx/conf.d
    - /etc/timezone:/etc/timezone:ro
    - /var/run/docker.sock:/tmp/docker.sock:ro
```

jwilder/nginx-proxy:latest 会自动加载conf.d下面的所有配置文件

#### 服务器


## 参考网站

### 文件处理 

(写入 换行)[http://www.programcreek.com/2011/03/java-write-to-a-file-code-example/]
(写入 tab)[http://stackoverflow.com/questions/2585337/how-to-use-tab-space-while-writing-in-text-file]
(写入 文件)[http://stackoverflow.com/questions/2885173/how-do-i-create-a-file-and-write-to-it-in-java]
(解析 换行)[http://www.programcreek.com/2011/03/java-read-a-file-line-by-line-code-example/] 
(解析 换行)http://stackoverflow.com/questions/5868369/how-to-read-a-large-text-file-line-by-line-using-java
(解析 ,分隔符处理)[http://stackoverflow.com/questions/29921059/java-read-large-text-file-with-separator]
(解析 tab)[http://stackoverflow.com/questions/18331696/reading-tab-delimited-textfile-java]

### 服务器操作 

( SFTP client 实例)[http://blog.csdn.net/is_zhoufeng/article/details/8306530]
(http post)[https://www.mkyong.com/java/how-to-send-http-request-getpost-in-java/]

### 服务器搭建

(Linux Centos 6.6搭建SFTP服务器)[http://blog.csdn.net/xinxin19881112/article/details/46831311]
(云服务器 ECS Linux Ubuntu 系统下开启 sftp 功能)[https://help.aliyun.com/knowledge_detail/41388.html]


(Add User to Docker Container)[http://stackoverflow.com/questions/27701930/add-user-to-docker-container]
