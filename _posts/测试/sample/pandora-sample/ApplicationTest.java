package com.test.sample;

import org.assertj.core.api.BDDAssertions;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.embedded.LocalServerPort;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit4.SpringRunner;

import com.taobao.pandora.boot.test.junit4.DelegateTo;
import com.taobao.pandora.boot.test.junit4.PandoraBootRunner;
import com.test.sample.domain.Student;

/**
 *
 * 集成测试，启动完整的spring context和tomcat
 *
 */
@RunWith(PandoraBootRunner.class)
@DelegateTo(SpringRunner.class)
@SpringBootTest(classes = { Application.class }, webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
// 利用 @TestPropertySource 可以很方便地设置测试需要的spring环境变量
@TestPropertySource(properties = { "management.port=0" })
// 激活test profile的bean和配置
@ActiveProfiles("test")
public class ApplicationTest {

    @LocalServerPort
    private int port;

    // spring boot endpoints的端口
    @Value("${local.management.port}")
    private int mgt;

    @Autowired
    private TestRestTemplate testRestTemplate;

    @Test
    public void shouldReturn200() {
        ResponseEntity<Student> entity = this.testRestTemplate
                .getForEntity("http://localhost:" + this.port + "/student/2", Student.class);

        BDDAssertions.then(entity.getStatusCode()).isEqualTo(HttpStatus.OK);

        Student student = entity.getBody();

        BDDAssertions.then(student.getName()).isEqualTo("student2");
    }

}
